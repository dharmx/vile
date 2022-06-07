#!/usr/bin/env zsh

## if the sound is muted then this function will return an image path of a muted sound icon
## otherwise it'll return an image of an un-muted sound
function status() {
    print $(pacmd list-sinks | awk '/\*/,EOF {print}' | awk '/muted/ {print $2; exit}')
}

## returns the volume level of the sound
function level() {
    pacmd list-sinks | grep -A 7 "\* index" | grep volume | awk -F/ '{print $2}' | tr -d ' ' | sed 's/%$//'
}

## mutes/unmutes the sound
function toggle() {
  local MUTED=$(pacmd list-sinks | awk '/\*/,EOF {print}' | awk '/muted/ {print $2; exit}')
  local DEFAULT_SOURCE=$(pacmd list-sinks | awk '/\*/,EOF {print $3; exit}')

  if [ "$MUTED" = "yes" ]; then
      pactl set-sink-mute "$DEFAULT_SOURCE" 0
  else
      pactl set-sink-mute "$DEFAULT_SOURCE" 1
  fi
}

## set volume a specific level (0-100%) 
## whatever you do, DO NOT pass floating point values
function setlevel() {
  local DEFAULT_SOURCE=$(pacmd list-sinks | awk '/\*/,EOF {print $3; exit}')
  pactl set-sink-volume "$DEFAULT_SOURCE" "$(truncate "$1")%"
}

## increases the volume level of the sound by 5%
function increase() {
  local DEFAULT_SOURCE=$(pacmd list-sinks | awk '/\*/,EOF {print $3; exit}')
  pactl set-sink-volume "$DEFAULT_SOURCE" +5%
}

## decreases the volume level of the sound by 5%
function decrease() {
  local DEFAULT_SOURCE=$(pacmd list-sinks | awk '/\*/,EOF {print $3; exit}')
  pactl set-sink-volume "$DEFAULT_SOURCE" -5%
}

function truncate() {
  echo "${1%.*}"
}

case "$1" in
    --toggle)
        toggle
        ;;
    --increase)
        increase
        ;;
    --decrease)
        decrease
        ;;
    --status)
        status
        ;;
    --level)
        level
        ;;
    --setlevel)
        setlevel "$2"
        ;;
    *)
        listen
        ;;
esac

# vim:ft=zsh:nowrap
