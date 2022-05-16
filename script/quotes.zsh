#!/usr/bin/env zsh

typeset DUNST_CACHE_DIR="$XDG_CACHE_HOME/dunst"
mkdir "$DUNST_CACHE_DIR" 2>/dev/null

typeset DUNST_QUOTES="$DUNST_CACHE_DIR/quotes.txt"
touch "$DUNST_QUOTES" 2>/dev/null

typeset DEFAULT_QUOTE="To fake it is to stand guard over emptiness. ── Arthur Herzog"

function add() { 
  [[ "$1" != "" ]] && print "$1" >> "$DUNST_QUOTES" 
}

function rm() { sed -i "$1d" "$DUNST_QUOTES" }

function rand() {
  local quote="$(cat $DUNST_QUOTES | shuf | head -n1)"
  [[ "$quote" == "" ]] && print "$DEFAULT_QUOTE" || print "$quote"
}

case "$1" in
  "add") add "$2";;
  "rm") rm "$2";;
  "rand") rand;;
  "all") cat "$DUNST_QUOTES";;
  *) print "$DEFAULT_QUOTE";;
esac


unset DUNST_CACHE_DIR DUNST_QUOTES DEFAULT_QUOTE

# vim:ft=zsh
