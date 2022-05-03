#!/usr/bin/env zsh

function _make_button() {
  print "(button :class 'vertigo-button vertigo-workspace vertigo-workspace-"$2"' :tooltip 'workspace: "$1" state: "$2"' :onclick 'bspc desktop --focus "$3"' '"$1"')"
}

function _wrap_yuck() {
  local buffered=""
  alias query="bspc query --names --desktops --desktop"
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
    buffered+=$(_make_button $_local[$index] $state $index)
  done
  print $buffered
  unalias query
}

function _make_box() {
  print "(box :orientation 'vertical' :class 'vertigo-box vertigo-desktop' :space-evenly true :tooltip 'workspaces' "$(_wrap_yuck)")"
}

function subscribe() {
  _make_box && bspc subscribe desktop node | while read -r _ do; _make_box done
}

function create() {
  local workspaces=(${$(bspc query --names --desktops --desktop .local)//$'\n'/ })
  workspaces+=$((${#workspaces} + 1))
  bspc monitor -d $workspaces[*]
}

function remove() {
  local workspaces=(${$(bspc query --names --desktops --desktop .local)//$'\n'/ })
  unset 'workspaces[-1]'
  bspc monitor -d $workspaces[*]
}

case $1 in
  subscribe) subscribe ;;
  create) create ;;
  remove) remove ;;
  *) print "Invalid option!" ;;
esac


# vim:ft=zsh
