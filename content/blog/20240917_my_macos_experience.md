---
title: "My macOS experience"
date: 2024-09-16T17:38:25Z
type: blog
draft: false
categories:
  - personal
tags:
  - macos
  - personal
---

Three weeks ago, my employer gave me a MacBook Pro to develop applications with Python and Large Language Models. This proved to be very tough on our Windows x86/x64 notebooks. However, my first steps with macOS were also tough. Up to that point, I had only worked with Linux and Windows desktops (and a brief detour to OS/2 back then). macOS was synonymous with "operating system for application development and design professionals" for me. I have to say, I was a little disappointed. Of course, a large part of my impression is due to my lack of experience with macOS, but in my opinion macOS is only usable after you have installed a dozen third-party applications (some are not free). Windows comes with most of that right out of the box with the PowerToys tools (free and open source).  

The hardware of a MacBook is really first class. There's absolutely nothing to complain about. And that's why I somehow fell in love with it :wink:

So let me try to reconstruct my first steps and describe the applications that are a must-have for me.

## brew

First of all, and this is already occasionally useful under Linux, is the package manager software `brew`. This allows you to install and update almost all programs under macOS conveniently via the command line. `brew` is super quick to install:

```sh
/bin/bash -c “$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)”
```

You simply can't get past this tool. brew [[1](https://brew.sh)] is an absolute must-have.

## Alfred / Raycast  

Spotlight is the name of the tool under macOS with which you can quickly start programs and switch to other windows using the key combination "CMD+Space". Spotlight can also be used to search for files.

Spotlight is not bad per se, but its range of functions is somewhat limited and does not offer what Microsoft PowerToys Run, for example, does. I therefore recommend Alfred [[2](https://alfred.app)] or Raycast [[3](https://www.raycast.com)]. These are both very powerful tools in which you can also integrate entire workflows and extensions. Both programs can be tried out free of charge, although Alfred is more limited in its free scope. Both tools are chargeable. I currently use Raycast because it offers more than Alfred in the free version and looks and feels more modern.

## Links

- [1] <https://brew.sh>
- [2] <https://alfred.app>
- [3] <https://www.raycast.com>
