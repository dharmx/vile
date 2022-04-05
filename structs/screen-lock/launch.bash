#!/usr/bin/env bash

color0='#23242A'
color8='#949494'
color1='#f87070'
color9='#f87070'
color2='#79dcaa'
color10='#36c692'
color3='#ffe59e'
color11='#ffe59e'
color4='#7ab0df'
color12='#7ab0df'
color5='#c397d8'
color13='#b77ee0'
color6='#70c0ba'
color14='#54ced6'
color7='#d4d4d5'
color15='#ffffff'


## Files and cmd
FILE="$XDG_CACHE_HOME/launch_lock.eww"
CONFIG="$XDG_CONFIG_HOME/eww/structs/screen-lock"
LOCKSCREEN_WALL="$XDG_CONFIG_HOME/eww/structs/screen-lock/assets/shuffle/backgrounds/background-night.jpg"

DEFAULT_DPMS=$(xset q | awk '/^[[:blank:]]*DPMS is/ {print $(NF)}')
LOCK_TIMEOUT=5 ### In Seconds
DUNST_INSTALLED=false && [[ -e "$(command -v dunstctl)" ]] && DUNST_INSTALLED=true
DUNST_IS_PAUSED=false && [[ "$DUNST_INSTALLED" == "true" ]] && DUNST_IS_PAUSED=$(dunstctl is-paused)

## Open widgets
run_eww() {
  eww -c "$CONFIG" open-many "time"   \
                     "user"           \
		             "system"
}

close_eww() {
  eww -c "$CONFIG" close "time"        \
                         "user"        \
                         "system"
}

prelock() {
  if [ "$DEFAULT_DPMS" == "Enabled" ]; then
    xset dpms "$LOCK_TIMEOUT"
  fi

  if [[ "$DUNST_INSTALLED" == "true" && "$DUNST_IS_PAUSED" == "false" ]]; then
    dunstctl set-paused true
  fi
}

lock() {
  i3lock --beep                                 \
         --image="$LOCKSCREEN_WALL"             \
         --color=00000000                       \
         --max                                  \
         --pointer=default                      \
         --ignore-empty-password                \
         --show-failed-attempts                 \
         --radius 40                            \
         --{key,bs}hl-color="$color4"EE         \
         --{verif,wrong,modif}-color=2E3440DD   \
         --separator-color="$color0"DD          \
         --wrong-text=" "                      \
         --wrong-color="$color1"EE              \
         --wrong-font="Iosevka Nerd Font"       \
         --wrong-pos 955:200                    \
         --wrong-size="100"                     \
         --greeter-color="$color12"EE           \
         --greeter-text=" "                    \
         --greeter-font="Iosevka Nerd Font"     \
         --greeter-size="80"                    \
         --greeter-pos 955:950                  \
         --no-modkey-text                       \
         --bar-indicator                        \
         --bar-direction=2                      \
         --bar-base-width 40                    \
         --bar-color 81A1C120                   \
         --bar-pos 0:1085                       \
         --bar-count 10                         \
         --pass-media-keys                      \
         --pass-screen-keys                     \
         --pass-volume-keys                     \
         --pass-power-keys
}

postlock() {
  if [ "$DEFAULT_DPMS" == "Enabled" ]; then
    xset dpms 0
  fi

  if [[ "$DUNST_INSTALLED" == "true" && "$DUNST_IS_PAUSED" == "true" ]]; then
    dunstctl set-paused false
  fi
}

## Launch or close widgets accordingly
if [[ ! -f "$FILE" ]]; then
  touch "$FILE"
  mpc pause
  playerctl pause
  prelock
  lock
  run_eww

  if [[ "$1" == "--no-screen-off" ]]; then
    xset dpms 0
  fi
else
  close_eww
  postlock
  rm "$FILE"
fi

# vim:ft=bash:nowrap
