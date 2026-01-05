---
categories:
- howto
date: '2026-01-13T09:42:00Z'
draft: false
tags:
- howto
- development
- recommendation
title: Taking Control of My Dotfiles with chezmoi
type: blog
---
Managing dotfiles is one of those things that starts as a quick weekend project and slowly evolves into a serious hobby. I’ve spent more hours than I’d like to admit tweaking my terminal colors or perfecting my shell aliases.

For a long time, I relied on a complex shell script to handle everything. It would move config files around, install software, and set up plugins. It worked fine when I only had one machine, but I started switching between macOS and various Linux distros, and my "simple" script became a maintenance nightmare. My goal was to have (mostly) identical environments on all my machines. 

That’s when I found chezmoi [1]. While it didn't necessarily make my setup less complex, it made the whole mess significantly more maintainable. 

## What is chezmoi?

At its core, chezmoi is a manager for your dotfiles. Instead of just symlinking files, it uses a 1:1 mapping between a source directory (usually a git repo) and your home directory. 

The real magic is in the templating. It allows you to use logic inside your configuration files. If I'm on my MacBook, I might want a specific alias setup or a different PATH variable than when I'm on my Linux server. 

Commonly used functions like `lookPath` (to check if a command exists) and OS-specific conditionals make your configs truly portable:

```toml
# .gitconfig.tmpl
[core]
{{- if lookPath "nvim" }}
    editor = nvim
{{- else }}
    editor = vim
{{- end }}
```

It's equally easy to handle different system paths or configurations between macOS and Linux. For example, setting up Homebrew in my `.zshrc.tmpl`:

```bash
{{- if eq .chezmoi.os "darwin" }}
if [ -f "/opt/homebrew/bin/brew" ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi
{{- else if eq .chezmoi.os "linux" }}
if [ -f "/home/linuxbrew/.linuxbrew/bin/brew" ]; then
  eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
fi
{{- end }}
```

With chezmoi, I can use a single file and let the template engine handle the differences based on variables like `.chezmoi.os` or custom data defined in my profile.

## Making it Public

I decided to host my dotfiles publicly on GitHub [2]. I’ll be honest: my setup probably won't suit anyone else. It’s tailored exactly to how I work. However, keeping it public means I can pull my entire environment onto any new computer in seconds. 

To make things even easier, I wrote a small wrapper script that allows me to kick off the setup on a remote machine via SSH. It’s very convenient  when I’m setting up a new VPS or a headless home server.

```bash
# setup-chezmoi-remote.sh
cat "$TEMP_CONFIG" | ssh "$SSH_TARGET" "
  sudo apt-get update && sudo apt-get install -y curl git
  mkdir -p ~/.config/chezmoi
  cat > ~/.config/chezmoi/chezmoi.toml
  sh -c \"\$(curl -fsLS get.chezmoi.io)\" -- init --apply --force $CHEZMOI_REPO
"
```

## Handling the Secret Stuff

Security is always the tricky part with public dotfiles. I use gopass [3] to manage my sensitive configuration files and passwords/keys. While chezmoi has built-in password management, I found it didn't quite fit my needs because I also need to deploy certain binary files that are stored securely.

My workflow looks like this:

1.  **Initialize**: I run `chezmoi init`. This triggers a `run_once_before` script that asks for a profile.

    ```bash
    # run_once_before_10-setup-config-from-gopass.sh.tmpl
    echo "Available config profiles:"
    echo "  1) basic  - Minimal setup"
    echo "  2) dev    - Full dev environment (Linux)"
    echo "  3) mac    - macOS workstation"

    read -r choice
    GOPASS_PATH="config/chezmoi/${CONFIG_NAME}.toml"
    gopass fscopy "$GOPASS_PATH" "$CONFIG_FILE"
    ```

2.  **Profile Selection**: The script asks me for a profile (like `mac`, `dev`, or `basic`).
3.  **Fetch Config**: It pulls the matching configuration directly from my gopass store.
4.  **Apply**: I run `chezmoi apply`.

I also added a custom script routine that fetches other sensitive files from gopass based on a local configuration file. 

```bash
# run_after_25-copy-gopass-files-local.sh.tmpl
while IFS=: read -r gopass_path dest_path; do
    dest_path="${dest_path/#\~/$HOME}"
    if gopass fscopy "$gopass_path" "$dest_path" 2>/dev/null; then
        chmod 600 "$dest_path"
        success "Copied: $gopass_path → $dest_path"
    fi
done < "$CONFIG_FILE"
```

Once those are in place, chezmoi takes over.

## Automation and Tooling

The rest of the heavy lifting is handled by chezmoi's lifecycle scripts: `run_before`, `run_after`, and `run_once`. 

I use these to automate my entire toolchain installation. On almost every system, I use Homebrew [4] to manage packages. My scripts check which tools are missing and install them based on the profile I selected, then chezmoi configures them. It’s a "set it and forget it" system that actually works.

If you’re still struggling with a giant `install.sh` script that breaks every time you update your OS, I highly recommend giving chezmoi a look. It takes some time to migrate, but the peace of mind is worth it.

## Sources

[1] chezmoi - <https://www.chezmoi.io/>  
[2] cloonix/dotfiles - <https://github.com/cloonix/dotfiles>  
[3] gopass - <https://www.gopass.pw/>  
[4] Homebrew - <https://brew.sh/>  
