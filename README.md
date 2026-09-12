# DESRU Linux Macro

>[!WARNING]
>## **NOT A FINISHED PROGRAM! Treat this as a proof of concept/beta**

## What it does so far:

Sends ONLY emulated mouse wheel up or down inputs once every 10ms (0.010 seconds) for a total inputs per second of 100

Only one of the scroll wheel emulations can be active at a time. __Only up or down. It will not allow for up and down at the same time__ 

## What needs to be added:

Blocking physical mouse wheel scrolling while the macro is active. I have gotten this working however it fucks up the mouse sensitvity outside of DOOM Eternal.

Potential fixes would be.
1. Requiring users to set their own mouse DPI for the virtual mouse

2. To use a Desktop Enviornment specific helper script to report if DOOM Eternal is the active/focused window and only grabbing the mouse device/activating the virtual mouse if it is
>[!NOTE]
>The change in mouse DPI does not seem to effect the ingame sensitvity of DOOM eternal (at least in my testing with some implementations it didn't) and is likley caused by how the game handles its mouse input on the backend

### **I will likely __ONLY__ continue working on this if the MDSR moderators approve of this being a potential solution for the lack of DESRU's macro on linux**

## Requirements

Tested on python 3.14.7 (likely works on most python 3 versions)

**Requires evdev**

## How to setup/use:

I recommend [__UV__](https://github.com/astral-sh/uv) for isolated virtual enviornments and this section will follow using uv. Venv or any other virtual envoirment manager for python can be used or no virtual envoirment at all (not recommended)
>[!IMPORTANT]
>**Your user MUST be in the input group to use this macro. To add yourself run `sudo usermod -aG input $USER`**

1. clone the git repo `{link here}`

2. Run `uv sync`

3. Edit `/src/desru-linux-macro/config.json` to set keybinds (Must be [evdev key names](https://python-evdev.readthedocs.io/en/latest/ecodes.html))

4. Run `uv run desru-linux-macro` to execute the python program
