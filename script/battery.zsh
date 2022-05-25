#!/usr/bin/env zsh

typeset level=$(cat /sys/class/power_supply/BAT0/capacity)

if [[ $level -ge 95 ]]; then
  print 
elif [[ $level -le 20 ]]; then
  print 
else
  print $level
fi

unset level

# vim:ft=zsh
