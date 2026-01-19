---
categories:
- howto
date: '2026-01-25T16:22:00Z'
draft: false
tags:
- git
- ssh
- development
- devops
title: 'SSH Agent Forwarding: A Facepalm Moment'
type: blog
---
I have been using SSH keys for nearly two decades. You would think I’d have the basics fully figured out by now. But recently, I had one of those "facepalm" moments where I felt a little stupid for not knowing something sooner.

Here is the situation: I needed my remote servers to access private Git repositories via SSH.

## The wrong way to do it

In the past, my workflow was clumsy. I created a specific, separate SSH key pair and deployed it to my remote systems. The idea was to avoid exposing my "main" private key. Still, leaving private keys scattered around on various servers increases the attack surface for my repositories.

## The simple solution: SSH Agent Forwarding

Instead of placing a key on the server, you just bring your local key with you. When the remote server needs to authenticate against GitHub, it forwards the request back to your local machine, asks your local `ssh-agent` for proof, and sends it back. The private key never leaves your laptop.

It is surprisingly easy to configure. You just need to tweak your SSH config file (`~/.ssh/config`) on your local machine, or use the `-A` option like `ssh -A my-web-server`:

```ssh
Host my-web-server
  HostName 192.168.1.50
  User myuser
  ForwardAgent yes
```

**A security note:** Never enable `ForwardAgent` with a wildcard host (like `Host *`). If you forward your agent to a malicious or compromised server, the administrator of that server could use your local agent to impersonate you elsewhere. Only enable this for specific hosts you trust [1].

On the remote server side, you just need to ensure the SSH daemon allows this. Usually, this is the default, but check `/etc/ssh/sshd_config`:

```ssh
AllowAgentForwarding yes
```

## The conflict with other ssh-agents

There was one small catch that took me some time to debug. I use `keychain` to manage my SSH keys. It’s a great tool, but it caused a conflict.

When I logged into the remote server, SSH set up the forwarding socket (stored in the environment variable `SSH_AUTH_SOCK`). However, my `.zshrc` script on the remote machine was blindly starting a *new* instance of `keychain`. This overwrote the `SSH_AUTH_SOCK` variable, breaking the forwarding connection to my laptop.

I had to update my shell configuration. Now, it checks if a socket already exists before trying to start `keychain`.

Here is the snippet I added to my `.zshrc`:

```sh
if [[ -z "$SSH_AUTH_SOCK" ]] && command -v keychain >/dev/null 2>&1; then
  if [ -f "/home/user/.ssh/id_ed25519" ]; then
    keychain --nogui /home/user/.ssh/id_ed25519
  elif [ -f "/home/user/.ssh/id_rsa" ]; then
    keychain --nogui /home/user/.ssh/id_rsa
  fi
  if [ -f "/home/user/.keychain/dev-sh" ]; then
    source /home/user/.keychain/dev-sh
  fi
fi
```

The logic is simple: `if [[ -z "$SSH_AUTH_SOCK" ]]` asks, "Is the socket variable empty?"

If it is empty, we start `keychain` as usual. If it is *not* empty (meaning SSH forwarding is already active), we skip the keychain startup entirely. This preserves the link to my local machine, allowing me to run `git pull` on the server using the keys on my laptop.

It’s a cleaner, more secure workflow. I just wish I had started using it a few years ago.

## References

[1] [GitHub Docs - Using SSH agent forwarding](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/using-ssh-agent-forwarding)
