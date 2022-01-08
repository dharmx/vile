#!/usr/bin/env bash

paused="$(dunstctl is-paused)"
set_paused="dunstctl set-paused"

case "$1" in
--toggle)
	if [[ "$paused" == "true" ]]; then
		eval "$set_paused false"
	else
		eval "$set_paused true"
	fi
	;;
--icon)
	if [[ "$paused" == "true" ]]; then
		echo ""
	else
		echo ""
	fi
	;;
esac
