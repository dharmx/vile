#!/usr/bin/env zsh

typeset -g MPD_DEFAULT="${XDG_CACHE_HOME:-~/.cache}/mpd/default.png"
typeset -g MPD_CACHE="${XDG_CACHE_HOME:-~/.cache}/mpd"
mkdir "$MPD_CACHE" 2>/dev/null

function clean_corrupt_mpd_caches() {
  pushd "$MPD_CACHE"
  for file in *
  do
    du "$file" | read -r size _
    [ $size -eq 0 ] && rm -rf "$file"
  done
  popd
}

function mpd_notify() { notify-send -i "$1" "$2" "$3" }

function handle_mpd_caching() {
  local audio_file="$(mpc --format='%file%' current)"
  if [[ "$1" == "get" ]]
  then
    [[ ! -f "$MPD_CACHE/$audio_file.png" ]] \
      && print "$MPD_DEFAULT" \
      || print "$MPD_CACHE/$audio_file.png"
  elif [[ "$1" == "subscribe" ]]
  then
    if [[ ! -f "$MPD_CACHE/$audio_file.png" ]]
    then
      mkdir -p "$MPD_CACHE/$(dirname "$audio_file")" 2>/dev/null &
      ffmpegthumbnailer                     \
        -i "$XDG_MUSIC_DIR/$audio_file"     \
        -o "$MPD_CACHE/$audio_file.png"     \
        -s 300                              \
        -q 1                                \
        -c png
      [ $? -eq 255 ] && rm -rf "$MPD_CACHE/$audio_file.png" || print "MPD: Caching $audio_file"
    fi
    while true
    do
      mpc --format='%file%' current --wait | read -r audio_file
      mkdir -p "$MPD_CACHE/$(dirname "$audio_file")" 2>/dev/null &
      if [[ ! -f "$MPD_CACHE/$audio_file.png" ]]
      then
        ffmpegthumbnailer                   \
          -i "$XDG_MUSIC_DIR/$audio_file"   \
          -o "$MPD_CACHE/$audio_file.png"   \
          -s 300                            \
          -q 1                              \
          -c png
        [ $? -eq 255 ] && rm -rf "$MPD_CACHE/$audio_file.png" || print "MPD: Caching $audio_file"
      fi
    done
  else
    print "MPD: Not implemented!"
  fi
}

function interface_mpd() {
  local state="$(mpc)"
  local art="$(handle_mpd_caching get)"
  local color="$(convert "$art" -depth 6 +dither -colors 8 -format "%c" histogram:info: | awk '{print $3}')"
  local color_fg="$(print "$color" | sed -n 6p | cut -c 1-7)"
  local color_bg="$(print "$color" | sed -n 1p | cut -c 1-7)"
  local info="$(mpc --format='
    {
      "artist":"%artist%",
      "album":"%album%",
      "title":"%title%",
      "track":"%track%",
      "duration":"%time%",
      "file":"%file%"
    }' current | jq --compact-output --monochrome-output ".art=\"$art\"|.color_fg=\"$color_fg\"|.color_bg=\"$color_bg\"")"

  case "$3" in
    artist|album|title|track|art|file) print "$info" | jq ".$3";;
    play|pause|next|prev|toggle) mpc --quiet $3;;
    duration) print "$info" | jq '.duration';;

    "repeat") mpc 'repeat' | tail -n1               \
      | awk --field-separator '   ' '{print $2}'    \
      | awk '{print $2}';;
    random) mpc random | tail -n1                   \
      | awk --field-separator '   ' '{print $3}'    \
      | awk '{print $2}';;
    single) mpc single | tail -n1                   \
      | awk --field-separator '   ' '{print $4}'    \
      | awk '{print $2}';;

    info) print "$info";;
    *) print "MPD: Not implemented!";;
  esac
}

function subscribe_to_mpd() {
  if [ "$1" = playback ]; then
    local old="$(mpc | sed -n 2p | awk '{print $1}')"
    print "$old"
    while sleep 0.3
    do
      local new="$(mpc | sed -n 2p | awk '{print $1}')"
      [ ! "$old" = "$new" ] && old="$new" && print "$old"
    done
  else
    interface_mpd _ _ info &
    [ $(mpc | sed -n 2p | awk '{print $1}') = '[paused]' ] \
      && eww update mpd_state='' \
      || eww update mpd_state=''
    while true
    do
      mpc current --wait &>/dev/null
      interface_mpd _ _ info &
    done
  fi
}

function connection() {
  wget -q --tries=10 --timeout=20 --spider http://google.com
  if [[ $? -eq 0 ]]; then
    echo "Online"
  else
    echo "Offline"
  fi
}

function interface_pctl() { 
  local metadata="$(playerctl metadata)"
  case "$3" in
    tojson)
      local artUrl="$MPD_DEFAULT"
      [ $(connection) = Online ] && artUrl='{{mpris:artUrl}}'
      playerctl metadata --format '{"url": "{{xesam:url}}","albumArtist":"{{xesam:albumArtist}}","length":"{{xesam:length}}","artist":"{{xesam:artist}}","discNumber":"{{xesam:discNumber}}","title":"{{xesam:title}}","autoRating":"{{xesam:autoRating}}","album":"{{xesam:album}}","artUrl":"'$artUrl'","trackid":"{{xesam:trackid}}","trackNumber":"{{xesam:trackNumber}}"}'
      ;;
    *) print "PCTL: Not implemented!"
  esac
}

function redirect() {
  if [ "$2" = "mpd" ]
  then
    interface_mpd $*
  elif [ "$2" = "pctl" ]
  then
    interface_pctl $*
  fi
}

case "$1" in
  interface) redirect $*;;
  sub_mpd) subscribe_to_mpd $2;;
  mpd_art) handle_mpd_caching $2;;
  *) print "Not implemented!";;
esac

unset MPD_CACHE MPD_DEFAULT

# vim:filetype=zsh
