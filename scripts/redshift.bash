#!/usr/bin/env bash

icon() {
  FILE="$XDG_CACHE_HOME/redshift_launch"
  if [[ ! -f "$FILE" ]]; then
    echo ""
  else
    echo ""
  fi
}

case "$1" in
  --toggle)
    eval "$XDG_CONFIG_HOME/eww/scripts/redshift-toggle.bash"
    ;;
  --icon)
    icon
    ;;
  *)
    echo "Invalid Option!"
    ;;
esac

# vim:ft=bash:nowrap
