#!/usr/bin/env bash

CACHE_PATH="$XDG_CACHE_HOME/eww/dunst/notifications.txt"
QUOTE_PATH="$XDG_CACHE_HOME/eww/dunst/quotes.txt"
DEFAULT_QUOTE="To fake it is to stand guard over emptiness. \u2500\u2500 Arthur Herzog"

mkdir -p "${CACHE_PATH:h}" "${QUOTE_PATH:h}" 2> /dev/null
touch "$CACHE_PATH" "$QUOTE_PATH" 2> /dev/null

INTERVAL='0.2'

function rand_quote() {
  local format
  format="$(tr '\n \t\r' 's' < "$QUOTE_PATH")"
  if [[ "$format" != "" ]]; then
    shuf "$QUOTE_PATH" | head -n1 
  else
    echo "$DEFAULT_QUOTE"
  fi
}

function empty_format() {
  echo "(box :class 'disclose-empty-box' :height 750 :orientation 'vertical' :space-evenly false (image :class 'disclose-empty-banner' :valign 'end' :vexpand true :path './assets/wedding-bells.png' :image-width 250 :image-height 250) (label :vexpand true :valign 'start' :wrap true :class 'disclose-empty-label' :text '$(rand_quote)'))"
}

function not_empty() {
  echo -n "(box :spacing 20 :orientation 'vertical' :space-evenly false"
  [[ "$(echo "$1" | tr -d ' ')" != "" ]] && echo -n "$1" || echo -n "$(empty_format)"
  echo ")"
}

case "$1" in
  rmid) sed -i "/:identity ':::###::::XXXWWW$2===::'/d" "$CACHE_PATH" ;;
  sub)
    old="$(tr '\n' ' ' < "$CACHE_PATH")"
    not_empty "$old"
    while sleep "$INTERVAL"; do
      new="$(tr '\n' ' ' < "$CACHE_PATH")"
      if [[ "$old" != "$new" ]]; then
        not_empty "$new"
        old="$new"
      fi
    done
    ;;
  quote) rand_quote ;;
  cls) echo > "$CACHE_PATH" ;;
esac

# vim:filetype=sh
