#!/usr/bin/env zsh

function make_button() {
  print "(button :class 'vertigo-button vertigo-workspace vertigo-workspace-"$2"' :tooltip 'workspace: "$1" state: "$2"' :onclick 'bspc desktop --focus "$3"' '"$1"')"
}

function wrap_yuck() {
  local buffered=""
  alias query="bspc query --desktops --desktop"
  # newlined str -> spaced str -> array, eg: "1\n2\n3" -> "1 2 3" -> (1 2 3)
  local _focused=(${$(query .focused)//$'\n'/ })
  local _urgent=(${$(query .urgent)//$'\n'/ })
  local _occupied=(${$(query .occupied)//$'\n'/ })
  local _local=(${$(query .local)//$'\n'/ })
  seq ${#_local} | while read -r index; do
    local current=${_local[$index]}
    local state="local"
    if [[ ${_occupied[(ie)$current]} -le ${#_occupied} ]]; then
      if [[ ${_focused[(ie)$current]} -le ${#_focused} ]]; then 
        _local[$index]="" && state="focused"
      else
        _local[$index]="" && state="occupied"
      fi
    elif [[ ${_urgent[(ie)$current]} -le ${#_urgent} ]]; then
      _local[$index]="" && state="urgent"
    elif [[ ${_focused[(ie)$current]} -le ${#_focused} ]]; then 
      _local[$index]="" && state="focused"
    else
      _local[$index]=$index && state="local"
    fi
    buffered+=$(make_button $_local[$index] $state $index)
  done
  print $buffered
  unalias query
}

function make_box() {
  print "(box :orientation 'vertical' :class 'vertigo-box vertigo-desktop' :space-evenly true :tooltip 'workspaces' "$(wrap_yuck)")"
}

make_box && bspc subscribe desktop node | while read -r _ do; make_box done

# vim:ft=zsh
