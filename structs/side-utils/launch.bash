#!/usr/bin/env bash

## Files and cmd
FILE="$XDG_CACHE_HOME/launch_side.eww"
CONFIG="$XDG_CONFIG_HOME/eww/structs/side-utils"

run_eww() {
  "$XDG_CONFIG_HOME"/eww/scripts/weather.py today fetch &
  polybar-msg cmd show
  polybar-msg cmd hide 
  eww -c "$CONFIG" open "sidecard"
}

close_eww() {
  polybar-msg cmd show
  eww -c "$CONFIG" close "sidecard"
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
