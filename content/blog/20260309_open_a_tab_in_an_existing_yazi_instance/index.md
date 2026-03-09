---
categories:
- howto
date: '2026-03-09T12:29:09Z'
draft: false
tags:
- howto
- personal
- kitty
- yazi
- terminal
- macos
title: Open a tab in an existing yazi instance
type: blog
---
Recently I have been trying to switch to a terminal only workflow. I am doing this partly for fun, but honestly the terminal is the fastest way to work with a computer once you get the hang of it. 

Because of this shift I am using Yazi [[1]](https://yazi-rs.github.io/). Yazi is a blazing fast terminal file manager written in Rust that offers asynchronous operations and a highly customizable interface.

## The problem with multiple windows

I wanted to integrate Yazi with the other tools on my macOS system. However I ran into a small annoyance. Every time I triggered a folder to open from another application it launched a completely separate instance of Yazi. I was looking for a way to open a new tab within an existing Yazi window instead of spawning a new process every single time.

## The solution using DDS

It turns out that Data Distribution Service is the way to go. Yazi uses this internally as a publish and subscribe messaging system between its instances.

When you launch Yazi normally it automatically generates its own internal ID. This is exposed inside a Yazi subshell as the environment variable `$YAZI_ID`. But you can also use the `--client-id` flag. This flag lets you define that ID in advance so your external scripts can reference it easily. It is important to note that this ID is not a standard process ID. It is a Data Distribution Service subscriber ID.

You can define your ID in a few ways. For example you can drop it right into your `.zshrc` file. Here is how you can set it up and send commands to it:

```sh
export YA_ID="$(date +%s)$RANDOM"
# or just hardcode it
export YA_ID="123456"

yazi --client-id "$YA_ID"

# then from elsewhere:
ya emit-to "123456" ~/Downloads
ya emit-to "123456" tab_create ~/Cloud
```

## Bringing it all together with Kitty

As an extra touch I wanted to bring my Kitty terminal to the front automatically using `osascript` on macOS. I wrote a quick script to handle the logic. It tries to open a tab in the existing instance. If that succeeds it brings Kitty into focus. If it fails because Yazi is not running yet it launches a fresh instance.

```sh
#!/bin/bash
MY_ID=12345678
FOLDER="${1:-$HOME}"

if ya emit-to "$MY_ID" tab_create "$FOLDER" 2>/dev/null; then
  # emit succeeded so the instance with that ID is running
  osascript -e 'tell application "System Events" to set frontmost of process "kitty" to true'
else
  # emit failed so there is no instance with that ID, launch one
  kitty yazi --client-id "$MY_ID" "$FOLDER" &
fi
```

This setup makes my workflow feel incredibly smooth. I get the speed of Yazi without cluttering my screen with a dozen different file manager windows.

## References

[1] Yazi - <https://yazi-rs.github.io/>  
