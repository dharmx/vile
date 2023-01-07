#!/usr/bin/env zsh

# Authored By dharmx <dharmx.dev@gmail.com> under:
# GNU GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007
#
# Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
# Everyone is permitted to copy and distribute verbatim copies
# of this license document, but changing it is not allowed.
#
# Permissions of this strong copyleft license are conditioned on
# making available complete source code of licensed works and
# modifications, which include larger works using a licensed work,
# under the same license. Copyright and license notices must be
# preserved. Contributors provide an express grant of patent rights.
#
# Read the complete license here:
# <https://github.com/dharmx/vile/blob/main/LICENSE.txt>

# Gist
# Controller script (from MVC pattern) for the vertigo widget.
# Gives out node_state (window_state?) and desktop_state (workspace_state?)

# read these https://specifications.freedesktop.org/wm-spec/wm-spec-1.3.html#idm46435614881776
# although you could guess what these mean by their prefixes and names
# Types:
#  - State
#  - Tag
#  - Layout
names=(STATE_FOCUSED STATE_OCCUPIED STATE_URGENT STATE_EMPTY TAG_HIDDEN TAG_STICKY TAG_PRIVATE TAG_LOCKED TAG_MARKED TAG_EMPTY LAYOUT_MONOCLE LAYOUT_TILED LAYOUT_FULLSCREEN LAYOUT_PSEUDO_TILED LAYOUT_FLOATING LAYOUT_EMPTY)
# NOTE: layouts include monocle as well and the rest are just node states. The names are not entirely misleading as
# NOTE: the STATE_* indicates desktop_state and LAYOUT_* indicates node_state hence the following todo.
# TODO: Clarify the diff between node_state and desktop_state items in the names array (rename).

pushd "$XDG_CONFIG_HOME/eww"

index=1 # IKR? ZSH arrays start with 1
jq --raw-output --compact-output '.desktops|values[][]' "./ewwrc" | while read -r icon
do
  # load the glyphs from the config and eval them into env vars
  eval "${names[$index]}='$icon'"
  index=$((index+1))
done

function _make_button() {
  #  --- --- --- -----------------------------------------
  # | 1 | 2 | 3 |                                         |
  #  --- --- --- -----------------------------------------
  # 1, 2 and 3 are the workspaces that are in the form of a button
  # this yuck literal represents that one workspace button, which is
  # then combined in a box
  # param $1: workspace label eg 1 / 2 / 3 ...
  # param $2: states out of urgent / occupied / focused / empty
  # param $3: actual workspace value as defined by the WM
  echo "{\"class\":\"vertigo-button vertigo-workspace vertigo-workspace-$2\",\"tooltip\":\"workspace: $1 state: $2\",\"onclick\":\"bspc desktop --focus $3\",\"label\":\"$1\"}"
}

function _wrap_desktop_yuck() {
  # combined 
  local buffered='['
  alias query="bspc query --names --desktops --desktop"
  # newlined str -> spaced str -> array, eg: "1\n2\n3" -> "1 2 3" -> (1 2 3)
  local _focused=(${$(query .focused)//$'\n'/ })
  local _urgent=(${$(query .urgent)//$'\n'/ })
  local _occupied=(${$(query .occupied)//$'\n'/ })
  local _local=(${$(query .local)//$'\n'/ })
  seq ${#_local} | while read -r index; do
    local current=${_local[$index]}
    local state="local"
    # ie -> [current in _occupied] -> returns a value greater than the
    # length of _occupied if it does not exist
    # if it exists then the index number is returned (neat)
    # you'll get the rest right?
    # translation of the line below: has(current, _occupied) < len(_occupied)
    if [[ ${_occupied[(ie)$current]} -le ${#_occupied} ]]; then
      # another thing to notice are priorities
      # i.e. occupied.focused is preferred over occupied.occupied
      if [[ ${_focused[(ie)$current]} -le ${#_focused} ]]; then 
        _local[$index]="$STATE_FOCUSED" && state="focused"
      else
        _local[$index]="$STATE_OCCUPIED" && state="occupied"
      fi
    elif [[ ${_urgent[(ie)$current]} -le ${#_urgent} ]]; then
      _local[$index]="$STATE_URGENT" && state="urgent"
    elif [[ ${_focused[(ie)$current]} -le ${#_focused} ]]; then 
      _local[$index]="$STATE_FOCUSED" && state="focused"
    else
      _local[$index]="$STATE_EMPTY" && state="local"
    fi
    buffered+=$(_make_button $_local[$index] $state $index)
    buffered+=","
  done
  buffered="${buffered::-1}]"
  echo "$buffered"
  unalias query
}

function _make_label() {
  # this is another functionality that this script provides i.e. the current node_state (focused)
  # it will indicate whether the node / window is tiled or, floating, etc.
  # param $1: node_label
  # param $2: node_state
  # param $3: node_state
  echo "{\"onmiddleclick\":\"bspc desktop --layout next\",\"class\":\"vertigo-button vertigo-node-button vertigo-node-button-$3\",\"tooltip\":\"node: $2\",\"label\":\"$1\"}"
}

function _wrap_node_yuck() {
  # gets the current focused node state and makes a label for it accordingly
  # which will then be evaluated by eww and rendered on the widget
  alias query="bspc query --nodes --node"

  # TODO: is there a way to not use jq?
  monocle=$(bspc query --tree --desktop | jq --raw-output .layout)

  if [ $(query .focused.tiled) ]; then 
    # this behaviour has been adapted from polybar i.e. if a desktop is not empty
    # then it will be checked whether that desktop is in monocle layout or not 
    # otherwise, it will show that the layout is empty (like if the desktop is in tiled instead)
    [ $monocle = monocle ] \
      && echo $(_make_label "$LAYOUT_MONOCLE" "monocle" "monocle") \
      || echo $(_make_label "$LAYOUT_TILED" "tiled" "tiled")
  elif [ $(query .focused.floating) ]; then 
    echo $(_make_label "$LAYOUT_FLOATING" "float" "float")
  elif [ $(query .focused.fullscreen) ]; then 
    echo $(_make_label "$LAYOUT_FULLSCREEN" "full" "full")
  elif [ $(query .focused.pseudo_tiled) ]; then 
    echo $(_make_label "$LAYOUT_PSEUDO_TILED" "pseudo" "pseudo")
  else
    # this behaviour has been adapted from polybar i.e. if a desktop is empty
    # then it will be checked whether that desktop is in monocle layout or not 
    # otherwise, it will show that the layout is empty (like if the desktop is in tiled instead)
    [ $monocle = monocle ] \
      && echo $(_make_label "$LAYOUT_MONOCLE" "monocle" "monocle") \
      || echo $(_make_label "$LAYOUT_EMPTY" "other" "other")
  fi
  unalias query
}

function subscribe_node() {
  # echo the focused node state if the WM state changes i.e. focus desktop / remove node / add node
  # (meaning focus to another desktop / close a window / open a window)
  # i.e. it continuously feeds the current state of the focused node / window into
  # a listener variable in a yuck file.
  _wrap_node_yuck && bspc subscribe \
    desktop_layout  \
    node_state      \
    node_remove     \
    node_add        \
    desktop_focus | while read -r _ do; _wrap_node_yuck done
}

function subscribe_desktop() {
  # similar to subscribe_node this feeds the current desktop states
  # if any desktop number has been increased / decreased
  # if any node / window has been moved to a different desktop
  _wrap_desktop_yuck && bspc subscribe \
    desktop_add     \
    desktop_remove  \
    desktop_focus   \
    node_transfer | while read -r _ do; _wrap_desktop_yuck done
}

function create() {
  # gets current total number of desktops and then add one to it
  # i.e. dynamically increase the workspace amount.
  local workspaces=(${$(bspc query --names --desktops --desktop .local)//$'\n'/ })
  workspaces+=$((${#workspaces} + 1))
  bspc monitor -d $workspaces[*]
}

function remove() {
  # opposite of the create function as defined above
  local workspaces=(${$(bspc query --names --desktops --desktop .local)//$'\n'/ })
  unset 'workspaces[-1]'
  bspc monitor -d $workspaces[*]
}

case $1 in
  subscribe_desktop) subscribe_desktop ;;
  subscribe_node) subscribe_node ;;
  create) create ;;
  remove) remove ;;
  *) echo "Invalid option!" ;;
esac

popd
unset index ${names[*]} names # redundant but clean ^_^


# vim:ft=zsh
