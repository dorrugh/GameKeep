#!/bin/bash
#
# /userdata/system/custom.sh for Batocera
# – Starts the timekeeper service
# – Launches the HTML/JS timer overlay
# – Then exec’s the emulator so ending the session returns to menu

export DISPLAY=:0

# 1) Start the timekeeper service in the background
nohup /userdata/game-keep/venv/bin/python \
  /userdata/game-keep/gamekeep.py \
  >/dev/null 2>&1 &

# 2) Finally exec the emulator; when it exits you drop back to the menu
exec /usr/bin/retroarch "$@"
