#!/usr/bin/env bash

STATUS=$(playerctl status)
if [[ "$STATUS" == "Playing" ]]; then
	echo " "
elif [[ "$STATUS" == "Paused" ]]; then
	echo "喇 "
else
    echo " "
fi

# vim:ft=bash:nowrap
