---
title: "Simple desktop switching with Autohotkey (Windows)"
date: 2025-01-29T16:00:17Z
type: blog
draft: false
categories:
  - howto
tags:
  - windows
  - desktop
  - productivity
  - development
  - autohotkey
---

Many years ago, I think it was in the 20th century 😉, Gnome in Linux already had virtual desktops and I loved them. In Windows there was no built-in solution afair/afaik. Most of you know what virtual desktops are, so here is a quick explanation: Virtual desktops are a software feature that allows you to organize and manage multiple desktop environments on a single computer. Essentially, they allow you to create several separate "workspaces" or "virtual screens" that you can switch between, even though you're still using the same physical monitor(s).

Today, every operating system has this feature, and you can easily switch between them with a keyboard shortcut. Except for Windows. You can cycle through your desktops with a shortcut, but you can't switch to a specific desktop, say desktop number 4. I usually have 3 to 4 workspaces, and on MacOS and Linux I use ALT+n to go to a specific workspace.

Back when Windows didn't have this feature, you could use Dexpot [1], which has been discontinued since 2016, or Virtuawin [2], which has been discontinued since 2021. Both tools were great and had a lot of features. For me, all I need is my ALT+n shortcut. So I found a solution with Autohotkey [3].

> AutoHotkey (AHK) is a free, open-source scripting language primarily for Windows, designed to help users automate repetitive tasks, create keyboard shortcuts, remap keys, and more. It's particularly popular for its flexibility and ease of use, even for those with minimal programming experience.

To make Windows virtual desktops accessible to Autohotkey, you will need a DLL file from this repository: <https://github.com/Ciantic/VirtualDesktopAccessor>. There is also a sample script that I used. There are also other AHK scripts that rely on this DLL [4].

## Make it work

Download the DLL provided at the link i mentioned before and download the example AHK script as well. Put both files into the same directory and adjust your shortcut for switching the desktop at the end of the example script. I changed it to:

```ahk
!1:: MoveOrGotoDesktopNumber(0)
!2:: MoveOrGotoDesktopNumber(1)
!3:: MoveOrGotoDesktopNumber(2)
!4:: MoveOrGotoDesktopNumber(3)
!5:: MoveOrGotoDesktopNumber(4)
```

This is the key combination for `ALT+n`.

The - imo - easiest way to start an autohotkey script on Windows startup, is putting a shortcut to that script into Windows' startup folder. You can easily go there with the command `shell:startup`.

## Links  

[1] <https://www.dexpot.de/>  
[2] <https://virtuawin.sourceforge.io/>  
[3] <https://www.autohotkey.com/>  
[4] <https://github.com/pmb6tz/windows-desktop-switcher>  
