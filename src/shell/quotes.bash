#!/usr/bin/env bash

# Authored By dharmx <dharmx@gmail.com> under:
# GNU GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007
#
# Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
# Everyone is permitted to copy and distribute verbatim copies
# of this license document, but changing it is not allowed.
#
# Permissions of this strong copyleft license are conditioned on
# making available complete source code of licensed works and
# modifications, which include larger works using a licensed work,
# under the same license. Copyright and license notices must be
# preserved. Contributors provide an express grant of patent rights.
#
# Read the complete license here:
# <https://github.com/dharmx/vile/blob/main/LICENSE.txt>

# Gist
# Controller script (from MVC pattern) for the vertigo + melody widget.
# Gives out random quotes

# load config values
DUNST_QUOTE_DIR="$(jq --compact-output --raw-output --monochrome-output .logger.quote_dir < "$XDG_CONFIG_HOME/eww/ewwrc")"
DUNST_QUOTE="$(jq --compact-output --raw-output --monochrome-output .logger.quote_name < "$XDG_CONFIG_HOME/eww/ewwrc")"
DEFAULT_QUOTE="$(jq --compact-output --raw-output --monochrome-output .logger.default_quote < "$XDG_CONFIG_HOME/eww/ewwrc")"

eval "DUNST_QUOTE_DIR=\"$DUNST_QUOTE_DIR\" && DUNST_QUOTE=\"$DUNST_QUOTE\""
DUNST_QUOTE_FULL="$DUNST_QUOTE_DIR/$DUNST_QUOTE"

mkdir "$DUNST_QUOTE_DIR" 2> /dev/null
touch "$DUNST_QUOTE_FULL" 2> /dev/null

function add() {
  # append a quote to a file
  # param $1: the quote that needs to be appended
  [ "$1" ] && echo "$1" >> "$DUNST_QUOTE_FULL"
}

function rm() {
  # remove a specific quote from a file by supplying an index
  # param $1: the quote that needs to be removed
  sed -i "$1d" "$DUNST_QUOTE_FULL"
}

function rand() {
  # get a random quote from the database file.
  # returns the fallback quote if it does not exist
  # or, if the database file is empty
  local quote
  quote="$(shuf < "$DUNST_QUOTE_FULL" | head -n1)"
  [ "$quote" ] || echo "$DEFAULT_QUOTE" && echo "$quote"
}

case "$1" in
  "add") add "$2" ;;
  "rm") rm "$2" ;;
  "rand") rand ;;
  "all") cat "$DUNST_QUOTE" ;;
  *) echo "$DEFAULT_QUOTE" ;;
esac

unset DUNST_QUOTE DUNST_QUOTES DUNST_QUOTE_DIR DUNST_QUOTE_FULL DEFAULT_QUOTE

# vim:ft=sh
