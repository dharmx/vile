#!/usr/bin/env zsh

typeset DUNST_LOG="$XDG_CACHE_HOME/dunst.log"
[ ! -f "$DUNST_LOG" ] && touch "$DUNST_LOG"

function create_cache() {
  local urgency
  case "$DUNST_URGENCY" in
    "LOW"|"NORMAL"|"CRITICAL") urgency="$DUNST_URGENCY";;
    *) urgency="OTHER";;
  esac

  local summary
  local body
  [[ "$DUNST_SUMMARY" == "" ]] && summary="Summary unavailable." || summary="$DUNST_SUMMARY"
  [[ "$DUNST_BODY" == "" ]] && body="Body unavailable." || body="$DUNST_BODY"

  local glyph
  case "$urgency" in
    "LOW") glyph="";;
    "NORMAL") glyph="";;
    "CRITICAL") glyph="";;
    *) glyph="";;
  esac
  print "(_card :class "\"disclose-card disclose-card-$urgency\"" :glyph_class "\"disclose-$urgency\"" :SL "\"$DUNST_ID\"" :L "\"dunstctl history-pop $DUNST_ID\"" :body "\"$body\"" :summary "\"$summary\"" :glyph "\"$glyph\"")" \
    >> "$DUNST_LOG"
}

function compile_caches() {
  local buffered=""
  cat "$DUNST_LOG" | while read -r card; do buffered+="$card "; done
  print "$buffered"
}

function make_literal() {
  print "(scroll :height 740 :vscroll true (box :orientation 'vertical' :class 'disclose-scroll-box' :spacing 10 :space-evenly false "$(compile_caches)"))"
}

function pop() {
  print "$(cat "$DUNST_LOG" | tail --silent --lines=+2)" > "$DUNST_LOG"
}

function drop() {
  print "$(cat "$DUNST_LOG" | head --silent --lines=-1)" > "$DUNST_LOG"
}

function clear_logs() { print > "$DUNST_LOG" }

function() critical_count() {
  cat "$DUNST_LOG" | grep "CRITICAL" | wc -l
}

function subscribe() {
  # monitor mouse buttons instead
  dbus-monitor interface='org.freedesktop.Notifications' | while read -r _ do; make_literal done
}

case "$1" in
  "pop") pop;;
  "drop") drop;;
  "clear") clear_logs;;
  "subscribe") subscribe;;
  "crits") critical_count;;
  *) create_cache;;
esac

unset DUNST_LOG

# vim:ft=zsh
