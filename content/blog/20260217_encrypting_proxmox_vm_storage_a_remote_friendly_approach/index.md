---
categories:
- howto
date: '2026-02-17T13:51:12Z'
draft: false
tags:
- howto
- self-hosting
- encryption
- proxmox
title: 'Encrypting Proxmox VM Storage: A Remote-Friendly Approach'
type: blog
---
I used to run a dedicated root server with a fully encrypted Proxmox installation. On boot, a dropbear SSH instance listens, waiting for me to unlock the disks before the actual OS loaded. It worked, but the monthly costs started to annoy me.

So, I made a switch. I bought a small Mini-PC with 64GB of RAM and placed it right next to a fiber internet connection (not my home). At first, I thought encryption wasn't necessary for this kind of setup. Since I'm not on-site all the time, the risk of it being stolen is existent. I realized I needed to encrypt the disks remotely without risking a non-booting system if anything went wrong.

My solution was a compromise. I would leave the Proxmox root partition unencrypted so the host is always reachable via SSH, but encrypt the actual VM data.

**Security disclaimer:** This protects against the most likely threat, a drive theft. However, because `/boot` and the root filesystem are unencrypted, an attacker with physical access and a Linux live USB could tamper with the initramfs or SSH daemon to capture the passphrase the next time you unlock. This is known as an "Evil Maid" attack. If they tamper with the system and you subsequently unlock it, the data is compromised. For a home lab in a semi-trusted location, I consider this an acceptable trade-off, but it's important to understand the distinction.

Since LUKS [1] doesn't allow in-place encryption, and I didn't want to rely solely on backups, I had to play a bit of a "shell game" with my storage. I used a second disk to shuffle data around, deleting and re-creating LVM thin pools as I went.

Here are my notes for future-me (and now-you) on how to pull this off, complete with a script to unlock everything with a single remote command.

## The Strategy

> **Backup:** Before proceeding, ensure you have a full backup of your data/vms. Disk encryption operations are irreversible and any mistakes can result in permanent data loss.

### Goal
The objective is to encrypt VM storage on both the NVMe and SSD drives while keeping the Proxmox OS unencrypted. This ensures the host boots and connects to the network automatically. Unlocking happens manually after boot by piping the passphrase from my local password manager.

### Final Storage Layout
Here is what the target architecture looks like. Note that the root OS lives on a standard partition, while the VM data lives inside encrypted containers.

```
nvme0n1p3 (953G)
└─ pve (VG)
   ├─ root (64G)               - Proxmox OS (unencrypted)
   ├─ swap (32G)               - Swap (encrypted at boot with random key)
   └─ encrypted (~857G LV)
      └─ [LUKS2]
         └─ pve-data-crypt → pve_encrypted/data (thin pool)
            └─ VM 100, 110 disks

sda (477G)
└─ [LUKS2]
   └─ ssdcrypt → ssd_encrypted (VG)
      └─ thinpool (thin pool)
         └─ VM 300 disks
```

### Encrypting Swap

The swap partition deserves special attention. If the host runs low on RAM, the kernel may swap out memory pages from VMs or even from the LUKS encryption process itself, writing decrypted data or sensitive keys to the unencrypted swap partition. An attacker who steals the drive could then analyze it to recover that data, potentially bypassing the VM encryption entirely.

Since hibernation isn't needed on a server, the cleanest fix is to encrypt swap with a random key generated fresh at each boot. The key is never stored on disk, so there is nothing to recover between reboots. Add the following line to `/etc/crypttab`:

```
swap /dev/pve/swap /dev/urandom swap,cipher=aes-xts-plain64,size=256
```

Then update `/etc/fstab` to reference the mapped device instead of the LV directly:

```
/dev/mapper/swap none swap sw 0 0
```

After a reboot (could take a long time, depending on the random entropy), verify with `swapon --show` that swap is active, and `cryptsetup status swap` to confirm it is encrypted.

## Step-by-Step Implementation

### Phase 0: Create Encrypted Volume on SSD
I started with `/dev/sda`, which was unpartitioned. I formatted it with LUKS2 and created a volume group and thin pool to use as temporary storage during the migration.

```bash
# Format SSD with LUKS2
cryptsetup luksFormat --type luks2 /dev/sda
# Enter passphrase (I used the same passphrase for NVMe later)

# Open encrypted volume
cryptsetup luksOpen /dev/sda ssdcrypt

# Create PV, VG, and thin pool
pvcreate /dev/mapper/ssdcrypt
vgcreate ssd_encrypted /dev/mapper/ssdcrypt
lvcreate -l 100%FREE -T ssd_encrypted/thinpool
```

*Note: LVM automatically reserves space for thin pool metadata, so you don't need to manually create the metadata volumes. However, monitoring metadata usage in production is recommended. If the metadata volume fills up (even while data space is still available), the pool can freeze or corrupt. Check with `lvs -a ssd_encrypted` and watch the `Data%` and `Meta%` columns.*

Next, I added this to Proxmox as **LVM-Thin** storage via the GUI:
*   **Datacenter → Storage → Add → LVM-Thin**
*   **ID:** `ssd-vms`
*   **VG:** `ssd_encrypted`
*   **Thin Pool:** `thinpool`
*   **Content:** Disk image

### Phase 1: Migrate VMs to SSD (Temporary)
With the SSD ready, I moved all VM disks off the NVMe. This was necessary so I could delete the existing unencrypted `pve/data` thin pool.

First, I shut everything down:
```bash
qm shutdown 110 && qm shutdown 300
sleep 30
ps aux | grep qemu   # Verify everything is stopped
```

Then, for each VM disk in the Proxmox UI:
1.  Go to **VM → Hardware → [disk] → Move Disk**.
2.  Target Storage: **ssd-vms**.
3.  Wait for the task to complete before starting the next one.

Once the disks were moved, I removed the old NVMe-backed storage configuration from Proxmox (**Datacenter → Storage → Remove** on `local-lvm`).

### Phase 2: Remove Old pve-data Thin Pool

Now for the scary part: deleting the original storage pool.

```bash
lvs pve               # Verify no vm-* volumes remain under pve/data
lvs | grep pve-data   # Verify 0.00% usage — all disks must be moved off!
lvremove /dev/pve/data
lvs | grep pve        # Should show only: root, swap
vgs pve               # Note free space (~857G became available)
```

### Phase 3: Create Encrypted Container on NVMe
I used the free space in the `pve` Volume Group to create a new Logical Volume. I then formatted that LV with LUKS2. Effectively, I made an encrypted container *inside* the existing LVM structure.

```bash
# Create LV using all free space in pve VG
lvcreate -l 100%FREE -n encrypted pve

# Format with LUKS2 and open
cryptsetup luksFormat --type luks2 /dev/pve/encrypted
# Enter passphrase
cryptsetup luksOpen /dev/pve/encrypted pve-data-crypt

# Create PV, VG, and thin pool inside the encrypted container
pvcreate /dev/mapper/pve-data-crypt
vgcreate pve_encrypted /dev/mapper/pve-data-crypt
lvcreate -l 100%FREE -T pve_encrypted/data

# Verify
cryptsetup status pve-data-crypt
vgs    # Should show: pve, pve_encrypted, ssd_encrypted
lvs pve_encrypted
```

I re-added this storage in the Proxmox UI:
*   **Datacenter → Storage → Add → LVM-Thin**
*   **ID:** `local-lvm`
*   **VG:** `pve_encrypted`
*   **Thin Pool:** `data`
*   **Content:** Disk image, Container

### Phase 4: Migrate VMs Back to NVMe
With the encrypted NVMe storage ready, I moved my main VM (110) back. I decided to keep VM 300 on the SSD permanently.

For each disk belonging to VM 110:
*   **VM 110 → Hardware → [disk] → Move Disk → local-lvm**

Finally, I fired everything back up:
```bash
qm start 110 && qm start 300
qm list
lvs pve_encrypted   # Confirm VM 110 disks present
lvs ssd_encrypted   # Confirm VM 300 disks present
```

## The Remote Unlock Workflow

After a reboot, the Proxmox OS comes up, but the encrypted containers are locked, meaning the VMs can't start. I didn't want to type passwords into a web console or store keys on the server.

I wrote a script that reads a passphrase from standard input (stdin), unlocks both drives, activates the volume groups, and starts the VMs. 

**The Script: `/home/claus/unlock-encrypted.sh`**

```bash
#!/bin/bash
set -e

echo "=== Unlocking Encrypted Storage ==="

read -r PASS

# SSD
if ! cryptsetup status ssdcrypt >/dev/null 2>&1; then
    echo "Unlocking SSD..."
    echo -n "$PASS" | cryptsetup luksOpen /dev/sda ssdcrypt -
    vgchange -ay ssd_encrypted
    sleep 2   # allow device nodes to fully populate
fi

# NVMe
if ! cryptsetup status pve-data-crypt >/dev/null 2>&1; then
    echo "Unlocking NVMe..."
    echo -n "$PASS" | cryptsetup luksOpen /dev/pve/encrypted pve-data-crypt -
    vgchange -ay pve_encrypted
    sleep 2
fi

echo "Starting VMs..."
for vmid in 100 110 300; do
    if qm status $vmid 2>/dev/null | grep -q "status: running"; then
        echo "VM $vmid already running"
    else
        qm start $vmid && echo "Started VM $vmid"
    fi
done

echo "Done"
qm list
```

Don't forget to make it executable:
```bash
chmod +x /home/claus/unlock-encrypted.sh
```

### Unlocking from my Workstation
I use `gopass` [2] locally to manage my secrets. I can pipe the password directly from my local machine into the script running on the server via SSH. This means the password never touches the Proxmox host's disk.

```bash
gopass show -o encryption/proxmox/disk | ssh -T pve 'sudo /home/claus/unlock-encrypted.sh'
```

**Prerequisite — sudo without a password prompt:** The `gopass` output is piped to the script via stdin. If `sudo` requires a password, it will consume that piped input instead of letting the script read it, causing authentication to fail. You must configure `NOPASSWD` for this specific command in `/etc/sudoers` on the Proxmox host (use `visudo`):

```
claus ALL=(ALL) NOPASSWD: /home/claus/unlock-encrypted.sh
```

Alternatively, run the script directly as root: `ssh -T root@pve '/home/claus/unlock-encrypted.sh'` — but only if root SSH login is explicitly enabled and secured with key-based authentication.

## Summary and Daily Use

This setup gives me peace of mind. If someone walks off with the server, they get the hardware and the base OS, but my data remains locked away.

Here are the commands I use to manage this setup:

```bash
# Unlock after reboot (from workstation)
gopass show -o encryption/proxmox/disk | ssh -T pve 'sudo /home/claus/unlock-encrypted.sh'

# Check encryption status
cryptsetup status ssdcrypt
cryptsetup status pve-data-crypt

# Check storage and VMs
vgs
qm list
```

It’s a bit more manual than a TPM-based auto-unlock, but for a home lab that I don't reboot often, the security trade-off is well worth it.

## References

[1] LUKS (Linux Unified Key Setup) - <https://gitlab.com/cryptsetup/cryptsetup>  
[2] gopass - The slightly more awesome standard unix password manager - <https://www.gopass.pw>
