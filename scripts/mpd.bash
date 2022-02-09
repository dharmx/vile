#!/usr/bin/env bash

## Get data
STATUS="$(mpc status)"
COVER="$XDG_CACHE_HOME/mpd/art.jpg"
DEFAULT="$XDG_CONFIG_HOME/mpd/default-art.jpg"
SHUFFLESTATUS=$(mpc | tail -n1 | awk -F '   ' '{print $3}' | awk '{print $2}')
REPEATSTATUS=$(mpc | tail -n1 | awk -F '   ' '{print $2}' | awk '{print $2}')
SINGLESTATUS=$(mpc | tail -n1 | awk -F '   ' '{print $4}' | awk '{print $2}')

## Get status
get_status() {
	if [[ $STATUS == *"[playing]"* ]]; then
		echo ""
	else
		echo ""
	fi
}

## Get song
get_song() {
	song=$(mpc -f %title% current)
	if [[ -z "$song" ]]; then
		echo "Offline"
	else
		echo "$song"
	fi
}

## Get artist
get_artist() {
	artist=$(mpc -f %artist% current)
	if [[ -z "$artist" ]]; then
		echo "Offline"
	else
		echo "$artist"
	fi
}

## Get time
get_time() {
	time=$(mpc status | grep "%)" | awk '{print $4}' | tr -d '(%)')
	if [[ -z "$time" ]]; then
		echo "0"
	else
		echo "$time"
	fi
}

get_ctime() {
	ctime=$(mpc status | grep "#" | awk '{print $3}' | sed 's|/.*||g')
	if [[ -z "$ctime" ]]; then
		echo "0:00"
	else
		echo "$ctime"
	fi
}

get_ttime() {
	ttime=$(mpc -f %time% current)
	if [[ -z "$ttime" ]]; then
		echo "0:00"
	else
		echo "$ttime"
	fi
}

## Get cover
get_cover() {
	ffmpeg -i "${XDG_MUSIC_DIR}/$(mpc current -f %file%)" "${COVER}" -y &> /dev/null
	STATUS=$?

	# Check if the file has a embedded album art
	if [ "$STATUS" -eq 0 ];then
		echo "$COVER"
	else
		echo "$DEFAULT"
	fi
}

toggle_shuffle() {
  if [ "$SHUFFLESTATUS" == "off" ]; then
		mpc random 1 &> /dev/null
	else
		mpc random 0 &> /dev/null
	fi
}

shuffle_status() {
	if [ "$SHUFFLESTATUS" == "off" ]; then
		echo "劣"
	else
		echo "列"
	fi
}

toggle_single() {
	if [ "$SINGLESTATUS" == "off" ]; then
		mpc single 1 &> /dev/null
	else
		mpc single 0 &> /dev/null
	fi
}

single_status() {
	if [ "$SINGLESTATUS" == "off" ]; then
		echo "凌"
	else
		echo "稜"
	fi
}

toggle_repeat() {
	if [ "$REPEATSTATUS" == "off" ]; then
		mpc repeat 1 &> /dev/null
	else
		mpc repeat 0 &> /dev/null
	fi
}

repeat_status() {
	if [ "$REPEATSTATUS" == "off" ]; then
		echo ""
	else
		echo "綾"
	fi
}

## Execute accordingly
if [[ "$1" == "--song" ]]; then
	get_song
elif [[ "$1" == "--artist" ]]; then
	get_artist
elif [[ "$1" == "--status" ]]; then
	get_status
elif [[ "$1" == "--time" ]]; then
	get_time
elif [[ "$1" == "--ctime" ]]; then
	get_ctime
elif [[ "$1" == "--ttime" ]]; then
	get_ttime
elif [[ "$1" == "--cover" ]]; then
	get_cover
elif [[ "$1" == "--toggle" ]]; then
	mpc -q toggle
elif [[ "$1" == "--next" ]]; then
	{ mpc -q next; get_cover; }
elif [[ "$1" == "--prev" ]]; then
	{ mpc -q prev; get_cover; }
elif [[ "$1" == "--shuffle" ]]; then
	toggle_shuffle
elif [[ "$1" == "--repeat" ]]; then
	toggle_repeat
elif [[ "$1" == "--single" ]]; then
	toggle_single
elif [[ "$1" == "--single-status" ]]; then
	single_status
elif [[ "$1" == "--repeat-status" ]]; then
	repeat_status
elif [[ "$1" == "--shuffle-status" ]]; then
	shuffle_status
elif [[ "$1" == "--seek-forward" ]]; then
	exec mpc -q seek +5 &> /dev/null
elif [[ "$1" == "--seek-backward" ]]; then
	exec mpc -q seek -5 &> /dev/null
fi

# vim:ft=bash:nowrap
