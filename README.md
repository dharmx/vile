<details>
  <summary><samp>screenshots and demo</samp></summary>
  <img src="./assets/.trash/montage.png" alt="montage"/>
  <img src="./assets/.trash/disclose.png" alt="disclose"/>
</details>

---

<samp>assumptions</samp>

```
- a functioning brain
- you are on arch
- you use bspwm
- you use sxhkd
- you use picom
- eww binary is already installed
```

<samp>env vars</samp>

```sh
export TERMINAL=st
export BROWSER=firefox
export VISUAL=nvim
export EDITOR=nvim
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_CACHE_HOME="$HOME/.cache"
export XDG_DATA_HOME="$HOME/.local/share"
export XDG_DOWNLOAD_DIR="$HOME/Downloads"
export XDG_MUSIC_DIR="$HOME/Music"
export XDG_PICTURES_DIR="$HOME/Pictures"

# SEE: https://wiki.archlinux.org/title/Xdg-utils
# SEE: https://wiki.archlinux.org/title/XDG_user_directories
# SEE: https://wiki.archlinux.org/title/Environment_variables
```

---

<samp>vertigo deps</samp>

```sh
yay -S zsh pamixer redshift rofi --needed
```

<samp>disclose deps</samp>

```sh
yay -S dunst-git gobject-introspection python python-pip --needed
pip install -r path/to/vile/requirements.txt
```

<samp>avatar deps</samp>

```sh
yay -S mpd mpc playerctl dunst-git gobject-introspection python python-pip \
  imagemagick --needed
pip install -r path/to/vile/requirements.txt

# NOTE: dunst, playerctl and mpd needs to be always running.
```

<samp>ocular deps</samp>

```sh
none
```

<samp>lumin deps</samp>

```sh
none
```

<samp>origin deps</samp>

```sh
none
```

<samp>melody deps</samp>

```sh
yay -S gobject-introspection python python-pip playerctl --needed
```

<samp>some important notes</samp>

```
- read this README twice.
- recheck and verify all vile/.config.json values.
- recheck and verify all _layout.yuck values.
- make an effort to parse and get a general idea of what each file does.
- ignore weather.py, pollution.py, puppet and horizon
- look for the fonts in https://github.com/dharmx/dots.sh/tree/main/local/share/fonts
- no need to install all of the fonts in the specified link
- search the scss files for font-family
```

---

<details>
  <summary><samp>sample .config.json (goes into ~/.config/eww)</samp></summary>

```json
{
  "player": {
    "mpd_cache": "$XDG_CACHE_HOME/mpd",
    "pctl_cache": "$XDG_CACHE_HOME/pctl",
    "default_art": "$XDG_CONFIG_HOME/eww/assets/cover.png"
  },
  "desktops": {
    "states": {
      "focused": "\uf963",
      "occupied": "\uf75a",
      "urgent": "\ufa44",
      "empty": "\uf75b"
    },
    "tags": {
      "hidden": "\ue95f",
      "sticky": "\ue9ad",
      "private": "\uea08",
      "locked": "\ue98f",
      "marked": "\ue9da",
      "empty": "\ue998"
    },
    "layouts": {
      "monocle": "\uf70d",
      "tiled": "\uf817",
      "fullscreen": "\uf749",
      "pseudo_tiled": "\uf752",
      "floating": "\uf70e",
      "empty": "\uf849"
    }
  },
  "network": {
    "interface": "CURRENTLY_NOT_IN_USE"
  },
  "notify": {
    "limit": 50,
    "interval": 0.5,
    "cache_path": "$XDG_CACHE_HOME/dunst/notifications.txt",
    "quote_path": "$XDG_CACHE_HOME/dunst/quotes.txt",
    "default_quote": "To fake it is to stand guard over emptiness. \u2500\u2500 Arthur Herzog",
    "timestamp": "%H:%M"
  },
  "tokens": {
    "openweather": "CURRENTLY_NOT_IN_USE",
    "github": "CURRENTLY_NOT_IN_USE",
    "gmail": "CURRENTLY_NOT_IN_USE"
  },
  "weather": {
    "latitude": null,
    "longitude": null,
    "units": "metric",
    "city": "Wonderland",
    "country_code": "lo",
    "lang": "en",
    "zip": "420699",
    "cache_dir": "$XDG_CACHE_HOME/weather",
    "icon_dir": "$XDG_CONFIG_HOME/eww/assets/weather"
  }
}
```

</details>

<details>
  <summary><samp>sample eww.yuck (goes into ~/.config/eww)</samp></summary>

```lisp
; ACTIVE Widgets
(include "./src/yuck/vertigo/_init.yuck") ; BSPWM specific
(include "./src/yuck/disclose/_init.yuck")

; INACTIVE Widgets
; NOTE: depends on disclose and vertigo currenty... this will change soon.
; (include "./src/yuck/ocular/_init.yuck")
; (include "./src/yuck/lumin/_init.yuck")
; (include "./src/yuck/melody/_init.yuck")
; (include "./src/yuck/origin/_init.yuck")
; (include "./src/yuck/avatar/_init.yuck")

; UNSTABLE Widgets
; (include "./src/yuck/puppet/_init.yuck") ; bspc node frontend
; (include "./src/yuck/horizon/_init.yuck")
```

</details>

<details>
  <summary><samp>sample dunstrc (goes into ~/.config/dunst)</samp></summary>

```ini
## NOTE: You may either have this config or find a way of simulating the rules-
## NOTE: such as [todo] [volume] [picom] as the special canned notifications are-
## NOTE: based off of the appname / rulename.
## SEE: handlers.py

[global]
background = "#11161b"
foreground = "#d4d4d5"
monitor = 0
follow = mouse
width = 480
height = 380
progress_bar = true
progress_bar_height = 25
progress_bar_frame_width = 3
progress_bar_min_width = 460
progress_bar_max_width = 480
highlight = "#79dcaa"
dmenu = /usr/bin/dmenu
indicate_hidden = true
shrink = true
transparency = 5
separator_height = 5
padding = 10
horizontal_padding = 10
frame_width = 3
frame_color = "#151a1f"
sort = true
idle_threshold = 0
font = Dosis,Iosevka Nerd Font 14
line_height = 2
markup = full
origin = "top-right"
offset = "50x50"
format = "<b>%s</b>\n%b"
alignment = left
show_age_threshold = 60
word_wrap = false
ignore_newline = true
stack_duplicates = true
hide_duplicate_count = true
show_indicators = true
icon_position = left
max_icon_size = 128
min_icon_size = 104
icon_theme = "custom,Reversal-green-dark,McMuse-green,Zafiro,McMuse,Papirus"
enable_recursive_icon_lookup = true
sticky_history = true
history_length = 50
browser = firefox
always_run_script = true
title = Dunst
class = Dunst
corner_radius = 0
notification_limit = 5
mouse_left_click = do_action
mouse_middle_click = close_current
mouse_right_click = context_all
ignore_dbusclose = true
ellipsize = end

[urgency_low]
timeout = 4
background = "#11161b"
frame_color = "#1f2429"
foreground = "#79dcaa"

[urgency_normal]
timeout = 8
background = "#11161b"
frame_color = "#1f2429"
foreground = "#7ab0df"

[urgency_critical]
timeout = 30
background = "#11161b"
frame_color = "#1f2429"
foreground = "#f87070"

[fullscreen_show_critical]
msg_urgency = critical
fullscreen = pushback

[volume]
appname = "volume"
summary = "*"
set_stack_tag = "volume"
format = "<b>%s</b>\n%b"

[microphone]
appname = "microphone"
summary = "*"
set_stack_tag = "microphone"
format = "<b>%s</b>\n%b"

[audiojack]
appname = "audiojack"
summary = "*"
set_stack_tag = "audiojack"
format = "<b>%s</b>\n%b"

[brightness]
appname = "brightness"
summary = "*"
set_stack_tag = "brightness"
format = "<b>%s</b>\n%b"

[shot]
appname = "shot"
summary = "*"
set_stack_tag = "shot"
format = "<b>%s</b>\n%b"

[shot_icon]
appname = "shot_icon"
summary = "*"
set_stack_tag = "shot_icon"
format = "<b>%s</b>\n%b"

[bar]
appname = "bar"
summary = "*"
set_stack_tag = "bar"
format = "<b>%s</b>\n%b"

[nightmode]
appname = "nightmode"
summary = "*"
set_stack_tag = "nightmode"
format = "<b>%s</b>\n%b"

[sxhkd]
appname = "sxhkd"
summary = "*"
set_stack_tag = "sxhkd"
format = "<b>%s</b>\n%b"

[layouts]
appname = "layouts"
summary = "*"
set_stack_tag = "layouts"
format = "<b>%s</b>\n%b"

[bspwm]
appname = "bspwm"
summary = "*"
set_stack_tag = "bspwm"
format = "<b>%s</b>\n%b"

[todo]
appname = "todo"
summary = "*"
set_stack_tag = "todo"
format = "<b>%s</b>\n%b"
new_icon = custom-to-do
background = "#161b20"
foreground = "#c397d8"

[picom]
appname = "picom"
summary = "*"
set_stack_tag = "picom"
format = "<b>%s</b>\n%b"

[spotify]
appname = "spotify"
summary = "*"
set_stack_tag = "spotify"
format = "<span size='x-large' font_desc='Cooper Hewitt 12' weight='bold' foreground='#79dcaa'>%s</span>\n%b"

[mpd]
appname = "mpd"
summary = "*"
set_stack_tag = "mpd"
format = "<span size='x-large' font_desc='Cooper Hewitt 12' weight='bold' foreground='#c397d8'>%s</span>\n%b"

[firefox]
appname = firefox
new_icon = firefox-default

[network]
appname = network
new_icon = network
summary = "*"
format = "<span size='x-large' weight='bold'>%s</span>\n<span font_desc='Cooper Hewitt,Iosevka Nerd Font 12'>%b</span>"
```

</details>
