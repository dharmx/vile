#!/bin/bash

CONFIG="$XDG_CONFIG_HOME/eww/ewwrc"
CACHE_DIR=$(jq --raw-output .github.cache_dir "$CONFIG")
eval "CACHE_DIR=${CACHE_DIR}"
USER_NAME=$(jq --raw-output .github.username "$CONFIG")
DATE=$(date +%F)

[ -f "$CACHE_DIR" ] || mkdir --parents "$CACHE_DIR"

fetch_user_info() {
  [ -f "$CACHE_DIR/users-$USER_NAME-$DATE.json" ] || curl --silent https://api.github.com/users/dharmx > "$CACHE_DIR/users-$USER_NAME-$DATE.json"
  [ -f "$CACHE_DIR/repos-$USER_NAME-$DATE.json" ] || curl --silent https://api.github.com/users/dharmx/repos > "$CACHE_DIR/repos-$USER_NAME-$DATE.json"
}

fetch_user_info
case "$1" in
  users) cat "$CACHE_DIR/users-$USER_NAME-$DATE.json" ;;
  repos) cat "$CACHE_DIR/repos-$USER_NAME-$DATE.json" ;;
esac

# vim:filetype=sh
