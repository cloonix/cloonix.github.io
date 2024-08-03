+++
title = 'Geforce Now Anti Idle Autohotkey Script'
date = 2024-08-03T19:05:06Z
tags = [ 'games', 'autohotkey', 'script' , 'autohotkey' ]
categories = [ 'howto' ]
type = "blog"
toc = 1
featured = 1
+++

I have been playing Geforce Now for the past two years and I absolutely love it. The convenience of being able to stream my favorite games without the need for high-end hardware has been a game-changer for me. Although i just bought a 4070 Ti. Right now it was a bad investment.  

But as much as I enjoy playing on Geforce Now, I sometimes encounter the issue of idle disconnects. To address this, I have created an Autohotkey script that keeps my session active even during periods of inactivity. For that my script switches back to the Geforce Windows and moves the mouse a bit. Whatever I was doing at that moment. For example: I'm looking up something on the Internet (about the game) or I reply to a text message. I forget about time and suddenly my game session got disconnected. Which could be very annoying if my game wasn't saved recently. This happens after a few minutes, 7 or 8 minutes it was, I guess.  

For those of you, who don't know AutoHotkey here is a small summary from ChatGPT :wink:

* Autohotkey is a scripting language that allows you to automate tasks and create hotkeys for various actions on your computer.
* It provides a simple syntax and a wide range of built-in functions, making it easy to write scripts for automating repetitive tasks or customizing your workflow.
* With Autohotkey, you can automate keystrokes, mouse movements, window management, and much more, making it a powerful tool for increasing productivity and efficiency.

## The Script

So here is my script for Autohotkey:

```autohotkey
; GeForceNOW

; keyboard commands only available if GFN is active
#IfWinExist ahk_exe GeForceNOW.exe

  ; turn timer on
  ^+k::
    ; timer action every 3 minutes
    Timer := 240 * 1000
    SetTimer, MoveTheMouse, %Timer%
    Menu, Tray, Icon, %A_ScriptDir%\assets\green.ico, 1
    SoundBeep, 750, 500
    SetKeyDelay, 50
  Return

  ; turn timer off
  ^+l::
    SetTimer, MoveTheMouse, Off
    Menu, Tray, Icon, %A_ScriptDir%\assets\red.ico, 1
    SoundBeep, 500, 500
    SetKeyDelay, 50
  Return
#IfWinExist

MoveTheMouse:
  ; helps with windows on different virtual windows desktop
  DetectHiddenWindows, On
  ; sleep timer (seconds) for random execution
  Random, rand, 90, 120
  SleepTimer := rand * 1000

  ; Mouse movement in pixels (also randomized)
  Random, x, -10, 10
  Random, y, -10, 10

  ; activates sleep timer
  Sleep, SleepTimer

  Idle := Timer + SleepTimer

  if (WinActive("ahk_exe GeForceNOW.exe"))
  {
    ; if window is active and system idle time exceeds Idle
    if (A_TimeIdle > Idle) {
      MouseMove, x, y, 10, R
    }

  } else if (WinExist("ahk_exe GeForceNOW.exe"))
  {
    ; if window exists
    WinActivate
    MouseMove, x, y, 10, R

  } else {
    ; if window does not exist, turn timer off
    SetTimer, MoveTheMouse, Off
    Menu, Tray, Icon, %A_ScriptDir%\assets\red.ico, 1
  }
Return
```

## Short explanation

The first hotkey ^+k (Ctrl + Shift + K) enables the timer. But it only works if a Geforce Now window is active. When this hotkey is pressed, a timer is set to trigger the MoveTheMouse label every 3 minutes.  I've added two icons in the asset folder, so i can see when the script is active. The second hotkey ^+l (Ctrl + Shift + L) turns off the timer.  

The script checks if the GeForce NOW window is active. If it is and the system idle time exceeds the calculated idle time, the mouse cursor is moved by the random x and y values. If the window exists but is not active, it activates the window and moves the mouse. If the window does not exist, the timer is turned off, and the system tray icon changes to red.  

If you have an suggestion or a question, you can get in touch with me on [Mastodon](https://chaos.social/@cloonix/) or [Matrix](https://matrix.to/#/@cloonix:matrix.org).  
