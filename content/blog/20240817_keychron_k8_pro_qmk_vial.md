---
title: "Keychron K8 Pro with vial-qmk support"
date: 2024-08-17T17:01:20Z
type: blog
featured: 1
categories:
  - howto
  - development
tags:
  - keychron
  - keyboard
  - qmk
  - vial
  - github
  - bluetooth
series:
  - keychron
---

A year ago I bought Keychron K8 Pro (RGB/ISO/DE). At that point I had zero experience with Keychron or with QMK [[1](https://qmk.fm/)]. QMK (Quantum Mechanical Keyboard) firmware is an open-source firmware for keyboards. It allows users to customize keymaps, macros, and various keyboard functionalities to suit their needs. QMK supports a wide range of keyboards and provides powerful features for advanced users. VIA [[2](https://www.caniusevia.com/)] is a graphical interface for QMK firmware that allows users to easily configure and customize their keyboards without needing to recompile the firmware. It provides a user-friendly way to manage keymaps, macros, and other settings in real-time.

But in my oppinion the real power of QMK unleashes if you write your customizations directly with QMK and compile your firmware on your own, or you have a vial-qmk firmware. What, Vial? No typo. Vial [[3](https://get.vial.today/)] has even more possibilities compared to VIA and a good UI for making changes on the fly.

But here is the problem: All wireless models from Keychron are not supported by the recent qmk firmware and thus not supported by Vial either. I spent a lot of time trying to merge the Keychron K8 Pro source with the qmk code, but I had no luck. Same for the Vial source code.  

Luckily a developer named adophoxia [[4](https://github.com/adophoxia)] made some changes to the vial-qmk source code which allows to use Bluetooth and Vial. Based on that code I added support for the K8 Pro (RGB/ISO/DE). I think you can easily add support for other K Pro models based on that branch.

One note at that point: The code of that branch is 8 months old. But qmk and vial were so stable at that time, i didn't have any problems. But new features are not working of course. And I was not able to merge the bluetooth branch with the most recent qmk/vial code... again :cry:  

## Steps to compile the firmare for the K8 Pro

I forked the code from adophoxia and only fetched the bluetooth branch [[5](https://github.com/adophoxia/vial-qmk/tree/keychron-bluetooth-PR)]. You can find the original link in the Link section at the end.  

I assume you are using an Ubuntu 24.x operating system. To compile the default vial firmware, follow these steps:

```sh
sudo apt install -y python3-pip pipx
pipx install qmk
cd ~/git
git clone https://github.com/cloonix/vial-qmk.git
cd vial-qmk
git checkout bluetooth
export PATH=$PATH:/home/user/.local/bin # qmk binary
qmk setup
make keychron/k8_pro/iso/rgb:vial
```

If you want to start with my personal build, which is definitely a good blueprint, you can clone and compile my custom keymap:

```sh
cd ~/git
git clone https://github.com/cloonix/vial-qmk-keymap.git
cd keyboards/keychron/k8_pro/iso/rgb/keymaps
ln -s ~/git/vial-qmk-keymap cloonix
cd ~/git/vial-qmk
make keychron/k8_pro/iso/rgb:cloonix
```

The resulting firmware (e.g. `keychron_k8_pro_iso_rgb_vial.bin`) you usually flash with the QMK Toolbox [[6](https://github.com/qmk/qmk_toolbox)]

## Conclusion

If you are using a Keychron Pro or Max model, you may encounter difficulties when trying to use Vial as a configuration tool. This is because the QMK source code currently does not support Bluetooth for Keychron keyboards, which means there is no Vial support either. However, with my code fork (with bluetooth support) and added support for the K8 Pro ISO keymap, you can adapt it to your Pro model.

## Links

[1] <https://qmk.fm/>  
[2] <https://www.caniusevia.com/>  
[3] <https://get.vial.today/>  
[4] <https://github.com/adophoxia>  
[5] <https://github.com/adophoxia/vial-qmk/tree/keychron-bluetooth-PR>  
[6] <https://github.com/qmk/qmk_toolbox>  
