#!/usr/bin/env zsh

source "$XDG_CONFIG_HOME/eww/script/config.zsh"
_set_vars

function category() {
  case "$1" in
    "unavailable") print "";;
    "unmanaged") print "";;
    "disconnected") print "";;
    "connecting") print "";;
    "connected") print "";;
    "deactivating") print "";;
  esac
}

function subscribe() {
  nmcli monitor | while read -r line; do
  done
}

case "$1" in
  "subscribe") subscribe "$2";;
  "category") category "$(nmcli general status | tail -n1 | awk '{print $1}')";;
  "wifistatus") wifi_status;;
  *) print "NOT IMPLEMENTED!";;
esac


_unset_vars

# vim:ft=zsh
