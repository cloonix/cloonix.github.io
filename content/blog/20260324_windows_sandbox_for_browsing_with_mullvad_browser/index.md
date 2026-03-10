---
categories:
- howto
date: '2026-03-24T09:03:00Z'
draft: false
tags:
- windows
- howto
- development
title: Windows Sandbox for Browsing with Mullvad Browser
type: blog
---
Windows Sandbox is a useful feature built into some editions of Windows. It gives you a clean, temporary, and mostly isolated environment that helps protect your host system. This is useful when you are testing scripts, trying unfamiliar software, or doing some web browsing in an ephemeral environment. It can help reduce malware risk, although it is not a bulletproof security boundary and it does not provide anonymity. When you close the sandbox, its local data is deleted.

In this quick guide, I will show you how to configure a custom Windows Sandbox that automatically installs Mullvad Browser at startup. Depending on your PC's performance, you can have a browsing sandbox up and running in about a minute.

## Setting Up the Host Folders

To make this work, I use two specific files on the host machine. In my setup, I keep my scripts in `T:\SandboxScripts`, and I keep the downloaded Mullvad Browser installer in `T:\Downloads`. You can adjust these paths to match your own drives. The idea is to map those host folders into the sandbox and then run an installation script automatically.

## The Installation Script

The most important part is the PowerShell script. I save this file as `logon.ps1` in my `T:\SandboxScripts` folder.

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force

$installers = @(
    "C:\Downloads\mullvad-browser-windows-x86_64-15.0.6.exe"
)

$installers | ForEach-Object { Start-Process $_ -ArgumentList "/S" -Wait }
```

First, the script bypasses the default execution policy so the code can run. Because it uses `-Scope Process`, this bypass is limited to the current PowerShell session and does not change the host's global execution policy. Then it defines a list of installer files. In this case, it points to the Mullvad Browser installer. Finally, it loops through that list and runs the installer silently using the `/S` argument. It waits for the installation to finish before moving on. You could add more tools to this list later, as long as each installer supports silent installation with the arguments you provide.

## The Sandbox Configuration

The second file is the Windows Sandbox configuration file. I save this as `sandbox.wsb` in the exact same `T:\SandboxScripts` directory.

```xml
<Configuration>
  <MappedFolders>
    <MappedFolder>
      <HostFolder>T:\SandboxScripts</HostFolder>
      <SandboxFolder>C:\SandboxScripts</SandboxFolder>
      <ReadOnly>true</ReadOnly>
    </MappedFolder>
    <MappedFolder>
      <HostFolder>T:\Downloads</HostFolder>
      <SandboxFolder>C:\Downloads</SandboxFolder>
      <ReadOnly>true</ReadOnly>
    </MappedFolder>
  </MappedFolders>
  <LogonCommand>
    <Command>powershell.exe -ExecutionPolicy Bypass -File C:\SandboxScripts\logon.ps1</Command>
  </LogonCommand>
</Configuration>
```

This XML file tells Windows how to start the sandbox. The `MappedFolders` section takes directories from the host machine and mounts them inside the sandbox at the `C:` drive level. I set both mapped folders to read-only so the sandbox can read from the host without writing changes back to it. That reduces the chance of accidentally modifying the original scripts or installers. Even so, avoid mapping sensitive files into the sandbox, because software running inside it can still read those files.

The `LogonCommand` section is the trigger. As soon as the sandbox finishes booting, it opens PowerShell and executes the `logon.ps1` script I created earlier.

## Launching the Environment

Once both files are saved, startup is as simple as double-clicking the `sandbox.wsb` file. Windows spins up the isolated environment, maps the local folders, and automatically runs the PowerShell script to install the browser. On my machine, this entire process takes about 60 seconds. Just keep in mind that while the sandbox is ephemeral, activity inside it can still be visible to websites, online services, your network, and your ISP. Mullvad Browser also does not create a VPN tunnel by itself; it is a privacy-focused browser, not a VPN client.

It's an easy example of what you can do with Windows Sandbox.
