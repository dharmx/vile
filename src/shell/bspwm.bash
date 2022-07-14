#!/usr/bin/env bash
# shellcheck disable=2154,1091

source "$XDG_CONFIG_HOME/bspwm/theme.bash"

wm_config=(
	border_width
	window_gap
	top_padding
	normal_border_color
	focused_border_color
	active_border_color
	presel_feedback_color
	split_ratio
	mapping_events_count
	borderless_monocle
	gapless_monocle
	borderless_singleton
	single_monocle
	center_pseudo_tiled
	presel_feedback
	honor_size_hints
	remove_disabled_monitors
	removal_adjustment
	remove_unplugged_monitors
	merge_overlapping_monitors
	automatic_scheme
	initial_polarity
	directional_focus_tightness
	top_monocle_padding
	right_monocle_padding
	bottom_monocle_padding
	left_monocle_padding
	pointer_motion_interval
	pointer_modifier
	pointer_action1
	pointer_action2
	pointer_action3
	click_to_focus
	swallow_first_click
	focus_follows_pointer
	pointer_follows_focus
	pointer_follows_monitor
	ignore_ewmh_focus
	ignore_ewmh_fullscreen
	ignore_ewmh_struts
)

function get_json() {
  local primed="{"
  for option in "${wm_config[@]}"; do
    primed+="\"$option\":\"$(bspc config "$option")\","
  done && primed="${primed::-1}" && primed+="}" && echo "$primed"
}

function json_subscribe() {
  local old new
  old="$(get_json)"
  while sleep "$1"; do
    new="$(get_json)"
    if [[ "$old" != "$new" ]]; then
      eval "$2"
      old="$new"
    fi
  done
}

function json_subscribe_preset() {
  local old new
  old="$(get_json)"
  echo "$old"
  while sleep "$1"; do
    new="$(get_json)"
    if [[ "$old" != "$new" ]]; then
      echo "$new"
      old="$new"
    fi
  done
}

function set_env() {
  local config_value
  for variable in "${wm_config[@]}"; do
    config_value="$(bspc config "$variable")"
    eval "$1$variable='$config_value'"
  done
}

function raw_subscribe() {
  local old_current new_current old_format
  set_env 'old_'
  while sleep "$1"; do
    set_env 'new_'
    for variable in "${wm_config[@]}"; do
      old_current="\$old_$variable"
      new_current="\$new_$variable"
      old_format="$(echo "$old_current" | cut --characters=2-)"
      eval "[[ \"$old_current\" != \"$new_current\" ]] && $2 \"$variable\" \"$old_current\" \"$new_current\""
      eval "$old_format=\"$new_current\""
    done
  done
}

function notify_choice() {
  notify-send -a layouts -i custom-sliders LayoutCTL "<span foreground='$yellow'>$1</span> has been set from <span font_weight='bold' foreground='$red'>$2</span> to <span font_weight='bold' foreground='$green'>$3</span>"
}

function echo_choice () {
  echo "$1 $2 $3"
}

case "$1" in
  --json|-j) get_json;;
  --sub-json|-sj) json_subscribe "$2" 'get_json';;
  --sub|-s) json_subscribe "${@:2}";;
  --sub-short|-ss) json_subscribe_preset "${@:2}";;
  --raw-sub|-rs) raw_subscribe "$2" 'echo_choice';;
  *) raw_subscribe 0.1 'notify_choice';;
esac

# vim:filetype=sh
