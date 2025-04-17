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

## Introduction

[Tailscale](https://tailscale.com/) has become my favorite solution for securely connecting to my devices. Tailscale is a zero-config VPN service that creates a secure mesh network between your devices using WireGuard. Though this blog post is not about tailscale itself, but how to set up a tailscale subnet on a GLiNet router to make the tailnet available to all connected clients. Please note: It's not about making the subnet available to the tailnet (hosts).

If you want to skip to the solution for the actual problem, skip to Step 4. 

## Purpose

By configuring your GLiNet router as a Tailscale subnet router, you allow all devices on your local network to access your Tailscale network without individual client installation. This is ideal for IoT devices and other hardware that can't run Tailscale directly, effectively extending your secure Tailscale network to every device in your home while maintaining Tailscale's security benefits.

## The subnet routing issue on the Beryl AX

I was happy to see that there is an tailscale client pre-installed on my Beryl AX. It worked instantly. But the subnet routing did not. And the main problem was, that i didn't find a solution on the web at first. 

First i tried to update the very old client on the Beryl AX. You can get the most recent package at: <https://pkgs.tailscale.com/unstable/#static>

### Step 1: SSH into your router

First, connect to your router via SSH and check the architecture:

```bash
ssh root@192.168.8.1
uname -a
```

### Step 2: Install the Tailscale package

```sh
cd /tmp 
curl -f -L https://pkgs.tailscale.com/unstable/tailscale_1.83.81_arm64.tgz -o tailscale_1.83.81_arm64.tgz
tar -zxvf tailscale_1.83.81_arm64.tgz
mv tailscale_1.83.81_arm64/tailscale* /usr/sbin/
```

Best to reboot the router now and re-login again.

## Step 3: Configure your Tailscale client

Log into your router's web interface and configure the Tailscale client. There you enable the subnet router option. You will get a warning, that you have to approve the advertised subnet routes: <https://login.tailscale.com/admin/machines>

## Step 4: The important part

You will notice, that the router itself can connect/ping all devices in the tailnet, but the connected clients cannot. The problem is, that the routing between the networks is missing and not set up by the GLiNet firmware. You have to go the Advanced Settings under: `System->Advanced Settings->Go To LuCI`.

Under `Network->Firewall` you have to create a new zone. Name it `tailscale`. Accept Input, Output and Forwarding and enable Masquerading and MSS clamping. In the menu `Covered Devices` you link that zone to the device `tailscale0`. Then you save & apply. 

Then you have to add the new zone to the `lan->wan` forwarding line. And you have to add `lan` and `wan` to the `tailscale` forwarding (masquerading enabled). 

Then you can fire up your tailscale again with the advertised routes.

```sh
tailscale up --advertise-routes=192.168.8.1/24
```

## Conclusion

With the latest version of Tailscale running on your GLiNet Beryl AX router, you now have a powerful subnet router that connects your home network to your Tailscale mesh network. This setup allows you to access your home devices securely from anywhere, without exposing them directly to the internet.

The ARM64 version of Tailscale ensures you get the best performance and latest features on your powerful GLiNet router. As an added bonus, having Tailscale built into your router means you don't need to run it on individual devices within your home network to access them remotely.

## Links

[1] [Tailscale Official Website](https://tailscale.com/)
[2] [Tailscale Downloads Page](https://pkgs.tailscale.com/stable/)
[3] [GLiNet Beryl AX Product Page](https://www.gl-inet.com/products/gl-mt3000/)
[4] [Tailscale Subnet Routes Documentation](https://tailscale.com/kb/1019/subnets/)