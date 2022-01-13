#!/usr/bin/env bash

WALLPAPERS="$XDG_CONFIG_HOME/eww/paths/wallpapers.txt"
CACHE="$XDG_CONFIG_HOME/eww/cache/current-wallpaper"
TOTAL_WALLPAPERS="$(wc -l < "$WALLPAPERS")"

next_path() {
    CURRENT=$(cat "$CACHE")
    if [[ "$CURRENT" -lt "$TOTAL_WALLPAPERS" && "$CURRENT" -gt 0 ]]; then
        echo "$((CURRENT + 1))" > "$CACHE"
    else
        echo 1 > "$CACHE"
    fi
    prepared_path "$(cat "$CACHE")"
}

previous_path() {
    CURRENT=$(cat $CACHE)
    if [[ "$CURRENT" -lt "$TOTAL_WALLPAPERS" && "$CURRENT" -gt 1 ]]; then
        echo "$((CURRENT - 1))" > "$CACHE"
    else
        echo "$TOTAL_WALLPAPERS" > "$CACHE"
    fi
    prepared_path "$(cat "$CACHE")"
}

current_path() {
    prepared_path "$(cat "$CACHE")"
}

prepared_path() {
    sed -n "$1p" "$WALLPAPERS"
}

apply_wallpaper() {
    TO_BE_APPLIED="$(prepared_path "$(cat $CACHE)")"
    feh --bg-scale "$TO_BE_APPLIED"
    dunstctl close
    dunstify -u low -i "$XDG_CONFIG_HOME/eww/assets/images/alert.svg"      \
                       "Changed wallpaper"                                                  \
                       "Applied $(basename "$TO_BE_APPLIED") as your new wallpaper!"
}

case "$1" in
    --next-path | -n)
      next_path
      ;;
    --previous-path | -p)
      previous_path
      ;;
    --current-path | -c)
      current_path
      ;;
    --apply-wallpaper | -a)
      apply_wallpaper
      ;;
    *)
      echo No such option!
      ;;
esac

# vim: ft=bash:nowrap
