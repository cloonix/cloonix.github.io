---
title: "Self-hosting Pangolin: A minimal setup guide"
date: 2025-12-25T09:33:24Z
type: blog
draft: false
categories:
  - self-hosting
tags:
  - pangolin
  - networking
  - security
  - guide
  - setup
  - docker
---

Pangolin is a powerful self-hosted platform for managing secure, zero-trust network access to your services.

I switched from Cloudflare to Pangolin primarily due to (free-tier) limitations and performance issues. Also, I encountered consistent connectivity problems during peak hours, particularly in the evenings, caused by Telekom's peer routing policies. These delays and throttling resulted in slow load times and unreliable access. By moving to Pangolin, I gained full control over my infrastructure with no limits, improved routing through self-hosted WireGuard tunnels, and consistent performance.

## Key benefits of Pangolin

*   **Self-Hosted Control**: Pangolin allows you to host the server yourself on your own hardware or VPS (such as Hetzner).
*   **Security through WireGuard**: The system utilizes secure WireGuard tunnels for traffic to maintain encrypted connections between clients and the server.
*   **Access rules**: You can define specific rules to allow or block traffic to your site. For instance, you can allow access to your services only from specific geographic regions (e.g., France, Germany, or Italy).
*   **Convenience**: You can instantly expose a local "in-dev" application to the public while keeping it safe behind Pangolin’s Single Sign-On (SSO). It even supports linking to existing OIDC providers, such as Pocket-ID.

## Prerequisites

- A dedicated server or VPS with a stable internet connection and a static public IP address.
- An internal service or application you intend to expose securely.
- Fundamental knowledge of Linux administration, firewall configuration, and Docker.

## Step 1: Configure DNS

Point your domain to your VPS public IP using A records:

```bash
pangolin.example.com  →  VPS1_PUBLIC_IP
blog.example.com      →  VPS1_PUBLIC_IP
git.example.com       →  VPS1_PUBLIC_IP
```

Verify propagation using:

```bash
dig pangolin.example.com
```

## Step 2: Set Up the Firewall

Allow essential ports for HTTPS and WireGuard traffic. On your VPS, run:

```bash
sudo ufw allow 80/tcp     # HTTP (Let's Encrypt)
sudo ufw allow 443/tcp    # HTTPS
sudo ufw allow 51820/udp  # WireGuard server
sudo ufw allow 21820/udp  # WireGuard clients
sudo ufw enable
```

> **Tip**: If using Hetzner Cloud, you can configure the firewall via the Cloud Console.

## Step 3: Install Pangolin

Download and run the official installer. The installer binary just helps you creating a basic `docker-compose.yml` configuration. 

```bash
curl -fsSL https://static.pangolin.net/get-installer.sh | bash
sudo ./installer
# i chose not to start the containers, so i do it manually
# plus, i used directory volumes for easy access to pangolin's config files
docker compose pull
docker compose up
```

**Personal flavor (optional)**: Ensure your `config.yaml` disables user organization creation. See: https://docs.pangolin.net/self-host/advanced/config-file - i couldn't find a way to set that flag within the `docker-compose.yml`.

```yaml
disable_user_create_org: true
```

## Step 4: Complete Initial Setup

Navigate to:

```
https://pangolin.example.com/auth/initial-setup
```

1. Create your admin account
2. Log in to the dashboard

## Step 5: Create a Site in the Dashboard

After logging in, register your first site through the Pangolin dashboard to enable proxy routing. Write down the ID and the Secret and/or the script command. 

## Step 6: Server Setup

Install the client agent (`newt`) on devices (sites) you want to connect from the outside. 

### Manual Installation

```bash
sudo curl -fsSL https://static.pangolin.net/get-newt.sh | bash
newt --id yyy --secret xxx --endpoint https://pangolin.example.com
```

### Systemd Service (Persistent)

Save as `/etc/systemd/system/newt.service`:

```ini
[Unit]
Description=Newt
After=network.target

[Service]
ExecStart=/usr/local/bin/newt --id 123 --secret abc --endpoint https://pangolin.example.com
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable newt
sudo systemctl start newt
```

## Step 7: Create a public resource

Similar to the Cloudflare setup, you create a resource and the local destination on the tunneled system, e.g. a docker container at `http://localhost:3000` and you define the domain through which the service should be reachable, e.g `https://docker.example.com`. 

Pangolin does the rest. Especially generating a SSL certificate and setup the forwarding/routing. 

## Conclusion

With this setup, you have a fully functional Pangolin server managing secure access to your services. Combine it with reverse proxies and Let’s Encrypt for full automation.

For more details, refer to the [official documentation](https://docs.pangolin.net/self-host/quick-install) or explore the [Docker setup examples](https://git.cmvps.de/claus/docker).