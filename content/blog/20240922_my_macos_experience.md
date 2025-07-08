---
title: "My macOS experience (an app collection)"
date: 2024-09-22T07:38:25Z
type: blog
featured: 0
draft: false
categories:
  - personal
tags:
  - macos
  - personal
toc: true
---

Three weeks ago, my employer gave me a MacBook Pro to develop applications with Python and Large Language Models. This proved to be very tough on our Windows x86/x64 notebooks. However, my first steps with macOS were also tough. Up to that point, I had only worked with Linux and Windows desktops (and a brief detour to OS/2 back then). macOS was synonymous with "operating system for application development and design professionals" for me. I have to say, I was a little disappointed. Of course, a large part of my impression is due to my lack of experience with macOS, but in my opinion macOS is only usable after you have installed a dozen third-party applications (some are not free). Windows comes with most of that right out of the box with the PowerToys tools (free and open source).  

The hardware of a MacBook is really first class. There's absolutely nothing to complain about. And that's why I somehow fell in love with it :wink:

So let me try to reconstruct my first steps and describe the applications that are a must-have for me.

## brew (package manager)

First of all, and this is already occasionally useful under Linux, is the package manager software `brew`. This allows you to install and update almost all programs under macOS conveniently via the command line. `brew` is super quick to install:

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

You simply can't get past this tool. brew [[1](https://brew.sh)] is an absolute must-have.

If you you want to dump all installed formulas and casks, use this command. You can then easily install the same set-up on a different machine by omitting the `dump` argument. 

```sh
brew bundle dump
```

## Alfred / Raycast (Spotlight replacement)

Spotlight is the name of the tool under macOS with which you can quickly start programs and switch to other windows using the key combination "CMD+Space". Spotlight can also be used to search for files.

Spotlight is not bad per se, but its range of functions is somewhat limited and does not offer what Microsoft PowerToys Run, for example, does. I therefore recommend Alfred [[2](https://alfred.app)] or Raycast [[3](https://www.raycast.com)]. These are both very powerful tools in which you can also integrate entire workflows and extensions. Both programs can be tried out free of charge, although Alfred is more limited in its free scope. Both tools are chargeable. I currently use Raycast because it offers more than Alfred in the free version and looks and feels more modern.

## Alt-tab

The window management in MacOS is not my thing and I can't get used to it. I want a computer that I can use without constantly having to use a mouse. But when I want to switch to another window on another desktop, the default Alt-Tab does not switch to that desktop.  

Alt-Tab [[4](https://alt-tab-macos.netlify.app)] helps with this. It makes the key combination similar to what you might be used to in Windows. Plus some additional and convenient features.

## Rectangle (tiling window manager)

If you use FancyZones with Microsoft's PowerToys you will need Rectangle (Pro) [[5](https://rectangleapp.com)] for macOS. It helps you to snap windows into pre-defined zones and it also supports layouts. A layout is a pre-defined set of apps and their positions. You can start a layout on a keyboard shortcut or on system startup.

Something similar can be achieved with Raycast. Raycast also supports the placement of windows in different zones and move windows between desktop/spaces (the latter is not possible with Rectangle). But Raycast does not support layouts.

## BetterDisplay (easy access to display options)

Again, not free, but I can't live without it. And I think the free version has enough for my daily work. BetterDisplay [[11](https://github.com/waydabber/BetterDisplay?tab=readme-ov-file)] offers a huge amount of options to control your built-in and external features. All I needed to do was enable or disable a connected display and, if enabled, make it the main display. You can define different display groups and activate individual displays with just a few clicks from the menu bar. You can also fine-tune almost every aspect of your display, including resolution, colours, contrast and so on.

## Ice (menu bar management)

Another thing that annoys me a lot in MacOS is the menu bar (at the top of the screen). If you have too many icons and a small display, it just hides the icons. You can sort them, but it doesn't help when space is limited. There are, of course, third-party apps. The best known is Bartender. But I don't like it for several reasons. One is the price. But there is an open source app that can help you: Ice [[10](https://github.com/jordanbaird/Ice)]. As well as some styling features, it allows you to show an extra bar on demand, which contains all the items you can't show or don't want to see all the time. It's also possible to hide icons all the time.

## Wireguard (VPN)

I don't need to explain Wireguard to you. But, maybe you didn't know that Wireguard [[6](https://apps.apple.com/de/app/wireguard/id1451685025?mt=12)] in macOS supports "on-demand" VPN configurations. It means, that the VPN tunnel is active for all Wifis, except for a list of known SSIDs.  

## borgbackup / borgmatic / vorta (deduplicated, encrypted, incrementally backups)

I love backups and I especially love borgbackup [[7](https://www.borgbackup.org)]. Unfortunately it does not run on Windows, but fortunately it does run on MacOS. borgmatic [[8](https://torsion.org/borgmatic/)] makes using borgbackup a little bit easier and vorta [[9](https://vorta.borgbase.com)] is a borgbackup GUI for Linux and macOS.

## rclone / fuse-t (connect cloud storage)

rclone [[13](https://rclone.org)] is a command line utility for managing files on cloud storage. It supports a lot of cloud providers. Even ones you have never heard of. It allows you to synchronise files between your local file system and the cloud. Similar usage to rsync. fuse-t [[12](https://www.fuse-t.org)] is a FUSE (Filesystem in Userspace) implementation which allows you to mount different filesystems on MacOS. It can be used in conjunction with rclone to mount cloud storage as if it were a local drive, making it easier to interact with your cloud files using standard file management tools. The big advantage of fuse-t is that it doesn't require any kernel extensions and it just works. It spawns an nfs server in the background and then you can connect to any rclone-supported cloud storage that rclone supports.  

## UTM (virtualization in macOS)

Another must-have for me. With UTM [[14](https://mac.getutm.app)] you can emulate other processor architecture or just simply run an ARM linux. Even run macOS parallel to your existing one. Usability is good and the virtualization worked flawlessly for me so far. And it's also free. But you can support the developers by buying the app from the Apple store.

## Commander One (Finder replacement)

Phew, I didn't expect the list to be this long. And I am still not finished.

I can't get used to the MacOS Finder. It's like a Windows Explorer experience. That's why I bought a lifetime licence of Total Commander [[15](https://www.ghisler.com/deutsch.htm)] a long time ago. Fortunately, there is something very similar for MacOS: Commander One [[16](https://commander-one.com)]. If you use rclone for cloud storage, you don't need the pro features. Otherwise, the pro features in Commander One are very handy if you want to connect them seemingly in your file browser. Commander One reminds me a lot of Total Commander. Surely by design.

## Shottr (screenshot tool)

I think we are coming to an end. So I make it short: Shottr [[17](https://shottr.cc)]:

> "Shottr is a tiny and fast mac screenshot tool with annotations, scrolling screenshots and cloud upload capabilities. Built with love and optimized for Apple silicon."

## Conclusion

I like my new MacBook, but mainly because the hardware is really great. Speakers, microphone, display, keyboard, trackpad, etc. It all works perfectly. And the battery life and performance are also wonderful.

But I can't really warm to macOS. I like the fact that it is based on Linux / Unix and thus has many strengths. But usability and a number of details (e.g. the confusing system administration and the confusing permission concept) disappoint me.

Just the list of applications that I had to install to improve my workflow was surprising. In a negative way.

You can tell that macOS and MacBooks come from an artistic (design, marketing) background. The hardware is top-notch, but the software is not as good. All in all, it's a bit overrated, but it will still be my main work tool.

Plus, I bought a Keychron V1 Max keyboard and I am working on a keymap to improve my workflow on macOS. It's a work in progress: <https://github.com/cloonix/qmk_keychron_v1_max>

If you have an suggestion or a question, you can get in touch with me on [Mastodon](https://chaos.social/@cloonix/) or [Matrix](https://matrix.to/#/@cloonix:matrix.org).  

## Links

- [1] <https://brew.sh>
- [2] <https://alfred.app>
- [3] <https://www.raycast.com>
- [4] <https://alt-tab-macos.netlify.app>
- [5] <https://rectangleapp.com>
- [6] <https://apps.apple.com/de/app/wireguard/id1451685025?mt=12>
- [7] <https://www.borgbackup.org>
- [8] <https://torsion.org/borgmatic>
- [9] <https://vorta.borgbase.com>
- [10] <https://github.com/jordanbaird/Ice>
- [11] <https://github.com/waydabber/BetterDisplay?tab=readme-ov-file>
- [12] <https://www.fuse-t.org>
- [13] <https://rclone.org>
- [14] <https://mac.getutm.app>
- [15] <https://www.ghisler.com/deutsch.htm>
- [16] <https://commander-one.com>
- [17] <https://shottr.cc>
