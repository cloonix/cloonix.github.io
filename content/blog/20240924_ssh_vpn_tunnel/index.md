---
title: SSH remote tunnel and a simple VPN solution
date: "2024-09-24T15:27:17Z"
type: blog
draft: false
---
Recently I wanted (or needed) to connect to a system that was not accessible from outside behind a firewall. This can be done via an SSH tunnel. It's actually simple, but the solution is perhaps not yet familiar to everyone.

So here is the initial situation. Three involved hosts:

- Host A: Firewalled, you want to access it
- Host B: Accessible via SSH (from Host A and C)
- Host C: From this host you want to connect to Host A

Host B serves as a kind of middleman and loops a tunnel from host C to host A:

⚠️ Use ssh keys on both sides (remote and local).

Step 1: On remote (firewalled) system. Host A connects to Host B:

```sh
ssh -l user-on-host-B -f -N -T -R22222:localhost:22 yourpublichost.example.com
```

`-f` puts the ssh connection in the background. `-N` means no remote command will be executed and `-T` disables pseudo-tty allocation. `-R` specifies the port on the remote host to which the tunnel is available.

Step 2: On local system. Host C connects to Host B:

```sh
ssh -l user-on-host-B -p yourpublichost.example.com -L 22222:localhost:22222
```

`-L` is the local port to which the tunnel is available and the destination at the remote host.

Step 3a: On local system. Host C connect to Host A via port tunnelling through Host B:

```sh
ssh -l user-on-host-A -p 22222 localhost
```

Step 3b: With `sshuttle` you can set up a VPN connection through this ssh tunnel (instead of step 3a):

```sh
sshuttle -vHr localhost:22222 0.0.0.0/0 --dns --no-latency-control
```

After step 3a, you can connect the firewalled system in the same way as it is available to the public. You can even tunnel all your traffic through the firewalled system as i describe in step 3b.

If you have an suggestion or a question, you can get in touch with me on [Mastodon](https://chaos.social/@cloonix/) or [Matrix](https://matrix.to/#/@cloonix:matrix.org).
