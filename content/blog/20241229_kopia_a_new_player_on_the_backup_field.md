---
title: "kopia: A new player on the backup field"
date: 2024-12-29T12:00:17Z
type: blog
draft: false
categories:
  - howto
tags:
  - backup
  - howto
  - borg
  - kopia
---

I love backups. Most people who know me probably know that. And I love borgbackup [1]. I've been using borgbackup for many years and I still think it's the best backup tool in the open source world. And in my opinion it beats all commercial solutions as well, provided you have the technical know-how.

BorgBackup, often referred to as borg, is a deduplicating backup program. It is designed to be efficient, secure, and versatile. Borg can:

- Perform fast, incremental backups.
- Use compression to reduce storage space.
- Encrypt backups to ensure data security.
- Support remote backups over SSH.
- Verify the integrity of backups.

These features make borg an excellent choice for both personal and professional backup needs.

But today it's about kopia [2].

## What is kopia?

Kopia is very similar to what borg has to offer. Personal taste aside, there are two main features that might make you consider using Kopia instead of or in addition to borg:

- Includes a graphical user interface (desktop and web application)
- Support for all operating systems
- Support for rclone remote backup targets
- More intuitive file/directory filters

## Quick start

When I took my first steps with Kopia, I was a little confused at first. In Kopia you create a repository. In that repository you can manage different snapshots. For example, you can have one snapshot for your Obsidian vault and another snapshot for your documents. In addition to the repository, you can define global policies for compression method, encryption, file/directory filters, and so on. The GUI is helpful, but the command line is also sufficient for advanced users.

So here is a quick start, assuming you already have a rclone destination configured. Mine is called `backup:` with the directory `kopia/macbook`:

```sh
# Setting global policies (my personal taste)
kopia policy set --global --keep-latest=12 --keep-hourly=24 --keep-daily=7 
kopia policy set --global --keep-weekly=4 --keep-monthly=12 --keep-annual=3
kopia policy set --global --compression=zstd
kopia policy set --global --ignore-identical-snapshots=true
kopia policy set --global --add-ignore '**/*[Tt]emp*'
kopia policy set --global --add-ignore '**/*[cC]ache*'
kopia policy set --global --add-ignore '**/.git*'

# Create the repository
kopia repository create rclone --remote-path=backup:kopia/macbook

# Create a snapshot
kopia snapshot create /Users/username/Obsidian
kopia snapshot create /Users/username/Documents
```

That's it. You can create incremental backups by simply running the last two commands as often and as often as you want:

```sh
kopia snapshot create /Users/username/Obsidian
kopia snapshot create /Users/username/Documents
```

Since I'm ignoring identical snapshots in my global policy, you'll only see new snapshots if something has changed. 

Here are some useful commands. They are fairly self-explanatory. 

```sh
kopia policy get --global
kopia snapshot list
kopia repository status
kopia policy get /Users/username/Obsidian
```

## Restoring a Backup/Snapshot

A backup that cannot be restored is useless. So always try to restore your backups from time to time. 

Restoring a kopia backup is quite simple. Find the ID of your snapshot with `kopia snapshot list` and then restore it to a different directory (for testing):

```sh
kopia restore 'kffbb7c28ea6c34d6cbe555d1cf80faa9' dest_restore
```

It's a bit more convenient than borgbackup. 

## Conclusion

I like kopia and use it on my Windows machine to frequently back up my Obsidian vault. In the long run, I haven't tested it enough to make it a replacement for borg. Also, kopia is still under very active development. Breaking changes could happen. 

However, if you ask me about my favorite backup solution(s), it's borg and kopia. 

If you have a suggestion or a question, you can contact me via Mastodon or Matrix.

## Links

[1] <https://www.borgbackup.org>  
[2] <https://kopia.io>