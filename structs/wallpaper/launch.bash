#!/usr/bin/env bash

## Files and cmd
FILE="$XDG_CACHE_HOME/launch_wallpaper.eww"
CONFIG="$XDG_CONFIG_HOME/eww/structs/wallpaper"

run_eww() {
  eww -c "$CONFIG" open-many "wallpaper"                \
                             "change"                   \
                             "backlightwallpaper"       \
                             "titlebar"                 \
                             "wallpapertime"
}

close_eww() {
  eww -c "$CONFIG" close "wallpaper"                \
                         "change"                   \
                         "backlightwallpaper"       \
                         "titlebar"                 \
                         "wallpapertime"
}

## Launch or close widgets accordingly
if [[ ! -f "$FILE" ]]; then
  run_eww
  touch "$FILE"
else
  close_eww
  rm "$FILE"
fi

# vim:ft=bash:nowrap
