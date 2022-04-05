#!/usr/bin/env bash

WALLPAPERS="$XDG_PICTURES_DIR/wallpapers"
PATH_CACHE_FRAGMENT="$XDG_CONFIG_HOME/eww/paths"

touch "$PATH_CACHE_FRAGMENT/$1"
ls "$WALLPAPERS/alto"/* >> "$PATH_CACHE_FRAGMENT/$1" 
ls "$WALLPAPERS/anime"/* >> "$PATH_CACHE_FRAGMENT/$1" 
ls "$WALLPAPERS/abstract"/* >> "$PATH_CACHE_FRAGMENT/$1" 
ls "$WALLPAPERS/chillop"/* >> "$PATH_CACHE_FRAGMENT/$1" 
ls "$WALLPAPERS/minimal"/* >> "$PATH_CACHE_FRAGMENT/$1"
ls "$WALLPAPERS/monokai"/* >> "$PATH_CACHE_FRAGMENT/$1"
ls "$WALLPAPERS/nord"/* >> "$PATH_CACHE_FRAGMENT/$1"
ls "$WALLPAPERS/outrun"/* >> "$PATH_CACHE_FRAGMENT/$1"
ls "$WALLPAPERS/pixel"/* >> "$PATH_CACHE_FRAGMENT/$1"
ls "$WALLPAPERS/other"/* >> "$PATH_CACHE_FRAGMENT/$1"
ls "$WALLPAPERS/scenery"/* >> "$PATH_CACHE_FRAGMENT/$1"
ls "$WALLPAPERS/gruvbox"/* >> "$PATH_CACHE_FRAGMENT/$1"
ls "$WALLPAPERS/poly"/* >> "$PATH_CACHE_FRAGMENT/$1"
ls "$WALLPAPERS/flowers"/* >> "$PATH_CACHE_FRAGMENT/$1"
ls "$WALLPAPERS/everforest"/* >> "$PATH_CACHE_FRAGMENT/$1"

# vim:ft=bash:nowrap
