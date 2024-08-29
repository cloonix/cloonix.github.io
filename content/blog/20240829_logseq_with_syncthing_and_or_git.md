---
title: "logseq with syncthing and/or git"
date: 2024-08-29T13:01:38Z
type: blog
draft: true
categories:
  - Howto
tags:
  - logseq
  - obsidian
  - syncthing
  - git
  - dev
---

Recently, I fell in love with [logseq](https://logseq.com/) [1]. At first glance, logseq confused me and didn't convince me. Later, after reading some articles and watching some videos, we became a couple :wink:

For my use case, I couldn't see logseq as a competitor or replacement for [Obsidian](https://obsidian.md/) [2], but as a complement. In my opinion, logseq is perfect for collecting notes and linking them together. On the other hand, Obsidian is my tool of choice when it comes to collecting topic-specific documents, such as software-specific commands that make my life easier and that I need or forget frequently.

Here are some interesting links that convinced me:

- [Get started with Logseq, my Daily Workflow](https://www.youtube.com/watch?v=uJclYLS4oHs)
- [50 logseq tips: Beginner to Expert in 6 Minutes](https://www.youtube.com/watch?v=r_tcDooayOo)
- [logseq Simple Queries - All the basics to filter what you need](https://www.youtube.com/watch?v=FePCqUN1Pgk)
- [logseq templates](https://docs.logseq.com/#/page/templates)
- [logseq git sync 101](https://github.com/CharlesChiuGit/Logseq-Git-Sync-101)

Before you start watching the videos about what you can do with logseq, a quick TL;DR about the sync mechanism this blog post is about:

## TL;DR

When I first started using logseq, it quickly became important to me to be able to work from different computers. As pointed out in the github repository [logseq git sync 101 by Charles Chiu](https://github.com/CharlesChiuGit/Logseq-Git-Sync-101) [3], git is the most robust way to synchronise your logseq graphs with multiple machines. But even here you have to bear in mind that you will quickly be confronted with annoying merge problems if you are not working with the latest commit or have forgotten to perform the commit/push on another computer.  

This is why Charles Chiu uses pre- and post-commit git hooks, which must be set up locally in each repository (as on each client). These git hooks from the `git-hooks` directory of the linked repository must be copied to the `./git/hooks/` subfolder and made executable (`chmod u+x`). This causes a `git pull` to be performed before each commit and then the `git push` after the commit.  

With these git hooks and the function of logseq to automatically perform a commit (e.g. every 30 minutes or when the application is closed), the problem formulated at the beginning is reduced.  

A pure synchronisation solution with git also has the advantage that you can really get it to work on all systems (including iOS/Android).  

## Why syncthing?

With the git solution, I didn't like the fact that I create a lot of commits in my repository and still run into problems when quickly switching computers. That's why I added syncthing to my synchronisation.  

[Syncthing](https://syncthing.net/) [4] is an open source file synchronisation software that makes it possible to synchronise files directly between devices without the need for a central server. It provides a secure and decentralised method of synchronising files over the internet or a local network.  

If you can do without iOS, which is the case for me, then you can also just work with syncthing. Synchronisation works better than with git, but you don't have the versioning provided by git.

I now combine both approaches:  

I usually have one computer that is always running. This computer uses the git hook mechanism. logseq makes an automatic commit every 60 minutes and pushes directly into the git repository.  
At the same time, syncthing is running on this computer, which shares the logseq folder with other computers. The following aspects are important here:

1. essential entries in the .gitignore file
2. and the exclusion of folders in Syncthing
3. make git case sensitive aware  

**.gitignore**  

```txt
logseq/bak
logseq/.recycle
.stfolder/
.stignore
*.tmp
```

**.stignore**  

```txt
**/.git*
```

Furthermore, it must be ensured that git is case sensitive. Otherwise there would be synchronisation conflicts with syncthing when changing upper/lower case of filenames/pages in logseq.  

```sh
git config core.ignorecase false
```

This change must be made on every computer that is to use git. I will not describe how to set up syncthing in this article.  

## Conclusion

Synchronisation with syncthing is actually sufficient. However, if you also want to use the advantages of a git repository, then the adjustments described above are necessary, as otherwise you will constantly create commits that should not be commits and/or have synchronisation conflicts with syncthing.  

In my case, four clients are now being synchronized via syncthing. One of these clients is almost always online and performs a commit (incl. push) every hour. Instead of this logseq client, you could also simply configure a Linux crontab to do this (provided Syncthing has also been set up there).  

If you have an suggestion or a question, you can get in touch with me on [Mastodon](https://chaos.social/@cloonix/) or [Matrix](https://matrix.to/#/@cloonix:matrix.org).  

## Links

[1] <https://logseq.com>  
[2] <https://obsidian.md/>  
[3] <https://github.com/CharlesChiuGit/Logseq-Git-Sync-101>  
[4] <https://syncthing.net/>  
