---
title: "kopia: A new player on the backup field"
date: 2024-12-29T15:00:17Z
type: blog
draft: true
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

[1] <https://www.borgbackup.org>  
[2] <https://kopia.io> 