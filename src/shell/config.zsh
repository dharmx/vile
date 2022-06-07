function _set_vars() {
  typeset -gx DUNST_CACHE_DIR="$XDG_CACHE_HOME/dunst"
  typeset -gx DUNST_LOG="$DUNST_CACHE_DIR/notifications.txt"

  typeset -gx DEFAULT_QUOTE="To fake it is to stand guard over emptiness. ── Arthur Herzog"
  typeset -gx DUNST_QUOTES="$DUNST_CACHE_DIR/quotes.txt"
  
  typeset -gx WIFI_INTERFACE="wlp0s20f3"
}

function _unset_vars() {
  unset DUNST_CACHE_DIR
  unset DUNST_LOG
  unset DUNST_QUOTES
  unset DEFAULT_QUOTE
  unset WIFI_INTERFACE
}
