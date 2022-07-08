#!/usr/bin/env bash

WIFI_INTERFACE="$(jq --compact-output --monochrome-output --raw-output .network.interface < "$XDG_CONFIG_HOME/eww/.config.json")"

function category() {
  case "$1" in
    "unavailable") echo "";;
    "unmanaged") echo "";;
    "using") echo "";;
    "disconnected") echo "";;
    "connecting") echo "";;
    "connected") echo "";;
    "deactivating") echo "";;
  esac
}

function make_tile() {
  [ "$(nmcli device status | grep "^$WIFI_INTERFACE" | awk '{print $3}')" = connected ] \
    || echo '(avatar_tile :L "nmcli device connect '"$WIFI_INTERFACE"'" :icon "'"$1"'" :main "Wi-Fi" :tooltip "'"$3"'" :class "avatar-eventbox-wifi avatar-eventbox-'"$2"'" :box_class "avatar-tile-'"$2"'" :class_main "avatar-main-'"$2"'" :class_icon "avatar-icon-'"$2"'")' \
    && echo '(avatar_tile :L "nmcli device disconnect '"$WIFI_INTERFACE"'" :icon "'"$1"'" :main "Wi-Fi" :tooltip "'"$3"'" :class "avatar-eventbox-wifi avatar-eventbox-'"$2"'" :box_class "avatar-tile-'"$2"'" :class_main "avatar-main-'"$2"'" :class_icon "avatar-icon-'"$2"'")'
}

function subscribe_to_wifi() {
  local data state icon
  data="$(nmcli device status | grep "^$WIFI_INTERFACE")" 
  state="$(echo "$data" | awk '{print $3}')"
  icon="$(category "$state")"
  make_tile "" "$state" "$state"

  nmcli device monitor "$WIFI_INTERFACE" | while read -r action; do
    data="$(echo "$action" | awk -F ': ' '{print $2}')"
    state="$(echo "$data" | awk '{print $1}')"
    icon="$(category "$state")"
    make_tile "$icon" "$state" "$data"
  done
}

case "$1" in
  "sub2wifi") subscribe_to_wifi;;
  *) echo "NOT IMPLEMENTED!";;
esac

unset WIFI_INTERFACE

# vim:ft=sh
