#!/usr/bin/env zsh

list=$(ls /usr/bin/ | grep -m 10 -i "$1")
buf=""
for l in $list ; do
  buf="$buf (button :class \"item\" :onclick \"$l &\" \"$l\")"
done
echo "(box :orientation \"v\" :spacing 5 :class \"apps\" :halign \"center\" :valign \"center\" $buf)" > ~/.config/eww/src/shell/search_items.txt
