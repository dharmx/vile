#!/usr/bin/env zsh

typeset STATUS="$(rfkill list | sed -n 2p | awk '{print $3}')"

case "$1" in
  "toggle") [[ "$STATUS" == "no" ]] && rfkill block all || rfkill unblock all;;
  "glyph") [[ "$STATUS" == "no" ]] && print "" || print "";;
esac

unset STATUS

# vim:ft=zsh
