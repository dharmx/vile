#!/usr/bin/env zsh 

typeset STATUS="$(rfkill list | sed -n 2p | awk '{print $3}')"
typeset AIRPLANE_MODE_OFF="$XDG_CONFIG_HOME/sxhkd/images/airplane/twotone_airplanemode_inactive_white_48dp.png"
typeset AIRPLANE_MODE_ON="$XDG_CONFIG_HOME/sxhkd/images/airplane/baseline_airplanemode_active_white_48dp.png"

notify_green() {
  notify-send -h "string:bgcolor:#79dcaa"                    \
            -h "string:fgcolor:#ffffff"                      \
            -h "string:frcolor:#00000000"                    \
            -h "string:image-path:$AIRPLANE_MODE_OFF"        \
            "$1"                                             \
            "$2"
}

notify_red() {
  notify-send -h "string:bgcolor:#f87070"                    \
            -h "string:fgcolor:#ffffff"                      \
            -h "string:frcolor:#00000000"                    \
            -h "string:image-path:$AIRPLANE_MODE_ON"         \
            "$1"                                             \
            "$2"
}

case "$1" in
  "toggle") 
    if [[ "$STATUS" == "no" ]]; then
      rfkill block all
      notify_green "Airplane mode" "Airplane mode is turned on."
    else 
      rfkill unblock all
      notify_red "Airplane mode" "Airplane mode is turned off."
    fi
  ;;
  "glyph") 
    if [[ "$STATUS" == "no" ]]; then
      print ""
    else 
      print ""
    fi
  ;;
esac

unset STATUS AIRPLANE_MODE_OFF AIRPLANE_MODE_ON

# vim:ft=zsh
