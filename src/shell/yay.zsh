#!/usr/bin/env zsh

function connection() {
  wget -q --tries=10 --timeout=20 --spider http://google.com
  if [[ $? -eq 0 ]]; then
    echo "Online"
  else
    echo "Offline"
  fi
}

function updates() {
  [ $(connection) = Online ] && yay --query --upgrades | wc --lines || print 
}

updates

# vim:ft=zsh
