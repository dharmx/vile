#!/usr/bin/env bash

DUNST_QUOTE_DIR="$(jq --compact-output --raw-output --monochrome-output .logger.quote_dir < "$XDG_CONFIG_HOME/eww/.config.json")"
DUNST_QUOTE="$(jq --compact-output --raw-output --monochrome-output .logger.quote_name < "$XDG_CONFIG_HOME/eww/.config.json")"
DEFAULT_QUOTE="$(jq --compact-output --raw-output --monochrome-output .logger.default_quote < "$XDG_CONFIG_HOME/eww/.config.json")"

eval "DUNST_QUOTE_DIR=\"$DUNST_QUOTE_DIR\" && DUNST_QUOTE=\"$DUNST_QUOTE\""
DUNST_QUOTE_FULL="$DUNST_QUOTE_DIR/$DUNST_QUOTE"

mkdir "$DUNST_QUOTE_DIR" 2>/dev/null
touch "$DUNST_QUOTE_FULL" 2>/dev/null

function add() { 
  [ "$1" ] && echo "$1" >> "$DUNST_QUOTE_FULL"
}

function rm() { 
  sed -i "$1d" "$DUNST_QUOTE_FULL" 
}

function rand() {
  local quote
  quote="$(shuf < "$DUNST_QUOTE_FULL" | head -n1)"
  [ "$quote" ] || echo "$DEFAULT_QUOTE" && echo "$quote"
}

case "$1" in
  "add") add "$2";;
  "rm") rm "$2";;
  "rand") rand;;
  "all") cat "$DUNST_QUOTE";;
  *) echo "$DEFAULT_QUOTE";;
esac

unset DUNST_QUOTE DUNST_QUOTES DUNST_QUOTE_DIR DUNST_QUOTE_FULL DEFAULT_QUOTE

# vim:ft=sh
