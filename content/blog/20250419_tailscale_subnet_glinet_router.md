---
title: "Tailscale subnet on a GLiNet Beryl AX (GL-MT3000)"
date: 2025-04-16T08:00:17Z
type: blog
draft: false
categories:
  - howto
tags:
  - tailscale
  - openwrt
  - vpn
  - glinet
  - network
---

[Tailscale](https://tailscale.com/) [1] has become my favorite solution for connecting my devices on different networks without the hassle of setting up dozens of WireGuard connections. Tailscale is a zero-configuration VPN service that uses WireGuard to create a secure mesh network between your devices. However, this blog post is not about Tailscale itself, but how to set up a Tailscale subnet on a GLiNet Beryl AX [3] router to make the Tailnet available to all connected clients. Note: It's not about making the subnet available to the tailnet (hosts).

If you want to skip to the solution for the actual problem, skip to Step 4. 

## Purpose


By configuring your GLiNet router as a Tailscale subnet router, you allow all devices on your local network to access your Tailscale network without having to install individual clients. This is ideal for IoT devices and other hardware that can't run Tailscale directly, effectively extending your secure Tailscale network to every device in your home while maintaining the security benefits of Tailscale.

## The subnet routing issue on the Beryl AX

I was happy to see that there was a Tailscale client pre-installed on my Beryl AX. It worked right out of the box. But the subnet routing did not. And the main problem was that I couldn't find a solution on the web. 

First i tried to update the very old client on the Beryl AX. You can get the most recent package at: <https://pkgs.tailscale.com/unstable/#static>

### Step 1: SSH into your router

First, connect to your router via SSH and check the architecture:

```bash
ssh root@192.168.8.1
uname -a
```

### Step 2: Install the Tailscale package

You get the package from the tailscale page at: <https://pkgs.tailscale.com/stable/> [3]

```sh
cd /tmp 
curl -f -L https://pkgs.tailscale.com/unstable/tailscale_1.83.81_arm64.tgz -o tailscale_1.83.81_arm64.tgz
tar -zxvf tailscale_1.83.81_arm64.tgz
mv tailscale_1.83.81_arm64/tailscale* /usr/sbin/
```

Best to reboot the router now and re-login again. Please be aware that a firmware upgrade overwrites the binaries and the previous steps have to be repeated. 

## Step 3: Configure your Tailscale client

Log into your router's web interface and configure the Tailscale client. There you enable the subnet router option. You will get a warning, that you have to approve the advertised subnet routes: <https://login.tailscale.com/admin/machines>. You should do that. 

## Step 4: The important part

You will notice, that the router itself can connect/ping all devices in the tailnet, but the connected clients cannot. The problem is, that the routing between the networks is missing and not set up by the GLiNet firmware. You have to go the Advanced (OpenWRT) Settings under: `System->Advanced Settings->Go To LuCI`.

Under `Network->Firewall` you have to create a new zone. Name it `tailscale`. Accept Input, Output and Forwarding and enable Masquerading and MSS clamping. In the menu `Covered Devices` you link that zone to the device `tailscale0`. Then you save & apply. 

Then you have to add the new zone to the (already existing) `lan->wan` forwarding line. And you have to add `lan` and `wan` to the `tailscale` forwarding (masquerading enabled). In other words: LAN traffic can be routed to the `wan` and `tailscale` network and `lan` and `wan` traffic can be routed to `tailscale`.

Then you can fire up your tailscale again with the advertised routes.

```sh
tailscale up --advertise-routes=192.168.8.1/24
```

But that's not all! Very important to execute on the GLiNet ssh command line as well:

```sh
tailscale set --stateful-filtering=false
```

## Conclusion

With the latest version of Tailscale and the firewall zone configuration running on your GLiNet Beryl AX router, you now have a powerful subnet router that connects your home network to your Tailscale mesh network. This setup allows you to securely access your home devices from anywhere without exposing them directly to the Internet.

As an added bonus, having Tailscale built into your router means you don't have to run it on individual devices within your home network to access them remotely.

## Links

[1] [Tailscale Official Website](https://tailscale.com/)
[2] [Tailscale Downloads Page](https://pkgs.tailscale.com/stable/)
[3] [GLiNet Beryl AX Product Page](https://www.gl-inet.com/products/gl-mt3000/)