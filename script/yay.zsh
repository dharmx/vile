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
  if [ $(connection) = Online ]; then
    yay --query --upgrades | wc --lines
  else
    print 
  fi
}

updates

# vim:ft=zsh
