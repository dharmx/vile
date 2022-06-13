#!/usr/bin/env bash

# WANTS: https://gitlab.archlinux.org/pacman/pacman-contrib
if ! pac=$(checkupdates 2> /dev/null | wc -l)
then
  pac=0
fi

# WANTS: https://github.com/Jguer/yay
if ! aur=$(yay -Qum 2> /dev/null | wc -l)
then
  aur=0
fi

updates=$((pac + aur))
[ "$updates" -gt 0 ] && echo "$updates" || echo ""

# vim:filetype=sh
