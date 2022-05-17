#!/usr/bin/env zsh

source "$XDG_CONFIG_HOME/eww/script/config.zsh"
_set_vars

function category() {
  case "$1" in
    "unavailable") print "";;
    "unmanaged") print "";;
    "using") print "";;
    "disconnected") print "";;
    "connecting") print "";;
    "connected") print "";;
    "deactivating") print "";;
  esac
}

function make_tile() {
  [ $(nmcli device status | grep ^wlp0s20f3 | awk '{print $3}') = connected ] \
    && print '(avatar_tile :L "nmcli device disconnect '$WIFI_INTERFACE'" :icon "'$1'" :main "Wi-Fi" :tooltip "'$3'" :class "avatar-eventbox-wifi avatar-eventbox-'$2'" :box_class "avatar-tile-'$2'" :class_main "avatar-main-'$2'" :class_icon "avatar-icon-'$2'")' \
    || print '(avatar_tile :L "nmcli device connect '$WIFI_INTERFACE'" :icon "'$1'" :main "Wi-Fi" :tooltip "'$3'" :class "avatar-eventbox-wifi avatar-eventbox-'$2'" :box_class "avatar-tile-'$2'" :class_main "avatar-main-'$2'" :class_icon "avatar-icon-'$2'")' 
}

function subscribe_to_wifi() {
  local data="$(nmcli device status | grep ^$WIFI_INTERFACE)"
  local state="$(print $data | awk '{print $3}')"
  local icon="$(category $state)"
  make_tile "" "$state" "$state"

  nmcli device monitor "$WIFI_INTERFACE" | while read -r action; do
    local data="$(print $action | awk -F': ' '{print $2}')"
    local state="$(print $data | awk '{print $1}')"
    local icon="$(category $state)"
    make_tile "$icon" "$state" "$data"
  done
}

case "$1" in
  "sub2wifi") subscribe_to_wifi;;
  *) print "NOT IMPLEMENTED!";;
esac

_unset_vars

# vim:ft=zsh
