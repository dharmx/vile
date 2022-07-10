#!/usr/bin/env bash

LEVEL="$(eww get EWW_BATTERY | jq --raw-output --compact-output --monochrome-output .BAT0.capacity)"
CRIT="$(jq --raw-output --monochrome-output --compact-output .battery.crit "$XDG_CONFIG_HOME/eww/.config.json")"
FULL="$(jq --raw-output --monochrome-output --compact-output .battery.full "$XDG_CONFIG_HOME/eww/.config.json")"
FULL_AT="$(jq --raw-output --monochrome-output --compact-output .battery.full_at "$XDG_CONFIG_HOME/eww/.config.json")"
CRIT_AT="$(jq --raw-output --monochrome-output --compact-output .battery.crit_at "$XDG_CONFIG_HOME/eww/.config.json")"

if [ "$LEVEL" -ge "$FULL_AT" ]; then
  echo "$FULL"
elif [ "$LEVEL" -le "$CRIT_AT" ]; then
  echo "$CRIT"
else
  echo "$LEVEL"
fi

unset LEVEL CRIT CRIT_AT FULL FULL_AT

# vim:ft=sh
