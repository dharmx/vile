<div align="center">

[![banner](./.github/readme/banner.png)](https://github.com/dharmx/vile)

[![issues](https://img.shields.io/github/issues/dharmx/vile?color=%23f87070&style=for-the-badge)](https://github.com/dharmx/vile/issues)
[![size](https://img.shields.io/github/repo-size/dharmx/vile?color=70c0ba&style=for-the-badge)](github.com/dharmx/vile) 
[![stars](https://img.shields.io/github/stars/dharmx/vile?color=c397d8&style=for-the-badge)](https://github.com/dharmx/vile/stargazers)
[![commits](https://img.shields.io/github/commit-activity/m/dharmx/vile?color=%2379dcaa&style=for-the-badge)](https://github.com/dharmx/vile/commits) 

</div>

---

# 👋 Introduction

Greetings, visitors. This is a repository of various useless GUI [widgets](https://www.merriam-webster.com/dictionary/widget) that may or, may not enchance the look of your current desktop interface.
I will walk you through each and every step of the installation process so, make sure to hit that lik- follow everything in a step-by-step fashion.

And if are here to borrow code then you may skip this README <samp>Obviously</samp>.

## 🚒 Procedure

A brief explanation of explanation (explanception!). This section is optional but it wouldn't hurt to gloss over it.

 - Introduction, brief description and greetings.
 - Procedure, explanception.
 - Showcase. Brief showcase, two screenshots of the project in action.
 - Assumptions. Conditions and constraints.
 - Structure. Project structure and design decisions.
 - <samp>MAKE IT STOP!</samp>
 - Dependencies. Modules, packages, scripts and resources that are required.
 - Configuration. The main shit.
 - Hacking. Advanced configuration.
 - Gallery.
 - End Goals.
 - Not Goals.
 - Tips. Useless shit.
 - FAQ.
 - Credits. Acknowledgements.
 - TODOs.
 - License.

---

## 🖼 Showcase

![demo](./.github/readme/demo.png)

## 🤔 Assumptions

List of conditions and constraints that are needed to be fulfilled.
This section solely to reduce some headaches.
This is done because I do not want to spend an extensive amount of time writing instructions for several Linux distributions.

I will choose Archlinux as a reference frame as I have only used Archlinux, Manjarno and EndeavourOS in the past.
So, following are roughly some assumptions that I will follow:

  - You are using either Archlinux or, an Arch-based distro like Manjaro.
  - You already have an editor, a browser and necessary utilities installed like `sudo, git, etc`.
  - You have `python` installed.
  - You are using an [AUR helper](https://wiki.archlinux.org/title/AUR_helpers).
  - You are using `bspwm` as your [window manager](https://wiki.archlinux.org/title/Window_manager).
  - You are using `sxhkd` as your [keyboard daemon](https://wiki.archlinux.org/title/Keyboard_shortcuts).
  - You use pulseaudio.

## 🌿 Structure

This is an important section for those who want to borrow some piece of functionality for use in their projets.
This section will paint a general idea of how stuff is being linked to one another so, you can have a general idea
for handling or, understanding a bug if one appears (which it will at some point).

---

### 🌿 General structure

```
├── assets
├── src
│   ├── scss
│   ├── shell
│   └── yuck
└── themes
```

 - `assets` contains images, graphics and svgs for use in the project.
 - `src.scss` contains all theming files. Theming is done using [SCSS](https://sass-lang.com/). So, all of the files in this directory will also be SCSS.
 - `src.yuck` contains markup files, all of which are of YUCK filetype.
 - `src.shell` contains various scripts.
 - `themes` this will also contain only SCSS files. <samp>Why not have them in src.scss then?</samp> Because organization. That's it.

### 🌿 `src` substructure

This structure will seem familiar to webdevs.

```
src
├── scss
│   ├── bolt
│   ├── lumin
│   └── vertigo
└── yuck
    ├── bolt
    ├── lumin
    └── vertigo
```

As you might have guessed.
The **modules** in the `scss` directory, style the classes that are defined in the yuck directory.
For instance, the module `lumin` will have `scss.lumin` which will contain styling specific to widgets defined in `yuck.lumin` only.

### 📚 Style Overrides

There is a `_override.scss` file which supplied for the purpose of overriding and testing your own stylings.
I have made this in order to contain different designs for the same widget.

### Layouts

There is a `_layout.yuck` in every widget module (eg: `src/yuck/lumin/_layout.yuck`) which acts like a mini-configuration. Tweak the values if you wish to do so 😉.

![transparent](./.github/readme/trans.png)

The above is the transparent version of the bar which is different to that shown in the showcase.

---

## 🔽 Dependencies

This section is divided into 2 parts:

 - Main Dependencies
 - Python Dependencies

### 🔽 Main Dependencies

Execute this in your terminal <samp>(if you dare.)</samp>.

```sh
yay --sync base-devel rustup python python-pip eww-git  \
  dunst bspwm sxkhd gobject-introspection imagemagick   \
  mpd mpc playerctl pamixer rofi redshift zsh jq --needed
# NOTE: use paru or, a AUR helper of your choice or, do the dirty work yourself.
```

 - Rustup is needed for compiling 
 - For [pipewire](https://wiki.archlinux.org/title/PipeWire) users you need to replace all of the matches of [`pamixer`](https://github.com/cdemoulins/pamixer) in 
   this repository with appropriate commands. You may use [`nvim-telescope's live-grep`](https://github.com/nvim-telescope/telescope.nvim) 
   feature to get the matches conveniently and elegantly.
 - For [dunst](dunst-project.org) you need to have have a specific configuration, which you can grab from the samples section.
 - And it should be a given that [`bspwm`](https://wiki.archlinux.org/title/Bspwm) and [`sxkhd`](https://wiki.archlinux.org/title/Sxhkd) are already configured.

### 🔽 Python Dependencies

Inspect the packages that you are about to install from [`requirements.txt`](https://github.com/dharmx/vile/blob/main/requirements.txt).
Then run the following command in your terminal while in `vile's` root.

```sh
pip install --requirement=requirements.txt
```

## Configuration

Start by placing vile into `~/.config` and rename `vile` to `eww`. Or, you can use symlinks as shown below.

```sh
git clone --depth 1 https://github.com/dharmx/vile.git ~/Downloads
ln -s ~/Downloads/vile ~/.config/eww
## do not remove ~/Downloads/vile
```

Now, right after doing that you need to make the scripts executable.

```sh
chmod +x ~/Downloads/vile/src/shell/*
```

---

This is a very very very important section. As the previous one, this section also divided into various parts.

 - Environment Variables.
 - API Setups
 - JSON / Script Configurations
 - Layout Configurations
 - Dependency Configurations
 - Headless Testing / Trial Run.

### Environment Variables

Start by reading the [xdg-utils](https://wiki.archlinux.org/title/Xdg-utils) and [xdg-vars](https://wiki.archlinux.org/title/XDG_user_directories) articles from the [ArchWiki](https://wiki.archlinux.org/).
Then you need to setup those variables by adding some lines in your [shellrc](https://www.tecmint.com/understanding-shell-initialization-files-and-user-profiles-linux/). Anyways, I will be using [ZSH](https://zsh.sourceforge.io/) 
for this so, we will add those environment variables by editing the `~/.zshenv` file first (create it if it doesn't exist).

Then just append these lines to the file.
```zsh
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_CACHE_HOME="$HOME/.cache"
export XDG_MUSIC_DIR="$HOME/Music"
export XDG_PICTURES_DIR="$HOME/Pictures"
```

On top of that you would need to add these as well.
```zsh
# NOTE: Add defaults of your choice as these may not be your taste.
export TERMINAL=st ## kitty for example
export BROWSER=firefox ## brave for example
export VISUAL=neovide ## nano for example
export EDITOR=nvim ## vim for example
```

See more info on what these variables do [here](https://wiki.archlinux.org/title/Environment_variables).

### API Setups

Starting with the easiest. Firstly you need to the [OpenWeather](https://home.openweathermap.org/users/sign_in) website and grab your [API key](https://rapidapi.com/blog/api-glossary/api-key/).
Do this by creating an account and logging into the site. Then go to the [`api_keys`](https://home.openweathermap.org/api_keys) tab and press on the generate button with a given name.
And if you already have a default key then use that instead.

Anyways, take a note of that key value as we will need it later.

### JSON and Script Configurations

Copy the ewwrc from the samples section and remove all of the comments. Then the first thing you'd need to do is add the tokens that you noted from the previous section.
For example the `tokens.openweather` field. 

> Note: You may skip this if you do not plan to use `clime and chrono` see the Galley section.

Take a look at the `location` key and see what method of fetching the location you want to select. If you have selected manual method then you'd need to fill out either
`latitude` and `longitude` or, `city` and `country_code` and `lang` fields. Learn more about these [here](https://openweathermap.org/history-bulk#parameter).
As for automatic, you do not need to do anything in the location field.

Then customize, change and tweak the values to you liking.

Now, open `src/shell/combine.bash` then edit and match the `CACHE_PATH`, `QUOTE_PATH`, `INTERVAL` and `DEFAULT_QUOTE` with the fields `notify.cache_path`, `notify.quote_path`,
`notify.default_quote` and `notify.interval` from `ewwrc`.

> Note: `combine.bash` is created to be an alternative for `logger.py` functions since it is quite slow.

### Layout Configurations

Moving on. Copy the sample `eww.yuck` from the sample section. Create the `eww.yuck` file and uncomment the widgets you need. You may take a look at the Gallery section.

As explained in the **Structure** section open the layout files of the modules that you enabled. For example if you have uncommented the vertigo module then, you would
need to open `src/yuck/vertigo/_layout.yuck` file and _customize_ the values like icons glyphs, labels, etc.

For example in the `bolt` widget if you change the `:volume_icon` field i.e. `` to a smiley face `:)` then

```lisp
;; NOTE: can be found in src/yuck/bolt/_layout.yuck
(_boltpctl :cover {pctl_sub["mpris:artUrl"]} 
           :label {pctl_sub["status"]} 
           :title {pctl_sub["xesam:title"]} 
           :artist {pctl_sub["xesam:artist"]} 
           :volume volume_level
           :volume_icon "" ;; to :volume_icon ":)"
           :status_cmd "playerctl play-pause"
           :status_icon {pctl_sub["status"] == "Playing" ? "" : ""})
```

![smile](./.github/readme/smile.png)

### Dependency Configurations

- Make sure you have playerctl running at all times. Execute `playerctld daemon` in your terminal to start playerctl.
- MPD needs to be running all times as well. Execute `mpd` in your terminal.
- Same goes for dunst. Only caveat is that you'd need a specific configuration for making it work with the `disclose` module.

#### Disclose: Notification Manager

There are some very specific things that you would need to do for setting up thee notification manager.
Firstly, grab or, inspect the sample `dunstrc` from the Samples section. Take a good look at the rulesets:

```ini
[volume]
appname = "volume"
summary = "*"
set_stack_tag = "volume"
format = "<b>%s</b>\n%b"

[firefox]
appname = firefox
new_icon = firefox-default
```

The above is an example of said ruleset. When a notification is sent by a certain application like for example firefox, they will send
some specific metadata on top of the usual message summary and message body. Which then we can use to tell apart the notifications sent from
firefox and other applications. This is done using the `appname` value.

We take that value and match it to these ruleset's `appname` field. And if you have looked at the above snippet carefully, you will notice that there is a
rule called `[firefox]` and within it there is a field called `appname` whose value is `firefox`.
Now, whenever Firefox browser sends us a notification it will be redirected to that ruleset.

Secondly, there is another field called `new_icon` which signifies that when Firefox sends a notification the notification icon will be replaced with an icon 
from your icon theme named `firefox-default.svg` (Yes, the extension will be truncated).

![firefox card](./.github/readme/firefox.png)

### Testing

This section will describe how you would know that the script work (trial-run). Since, if the scripts work then most probably the will work too.
These (might) be automated later in the near future with unit testing.

Before we begin I would urge you to recheck and verify if all the XDG variables have been set or not. Source the `~/.zshenv` again if you are not confident.
Go to the root of the vile repo. Then change the directory to where all of the scripts are located at `cd src/shell`.
 - <samp>logger.py</samp>: Run this using `./logger.py init` which will initialize the [dbus](https://www.freedesktop.org/wiki/Software/dbus) eavesdropper.
   Now, open another terminal and run `./logger.py subscribe` then open another terminal and type `notfy-send hello`. Now, if something appears in the second 
   terminal then the script is working.

   ```lisp
   (box :spacing 20 :orientation 'vertical' :space-evenly false (_cardimage :class 'Spotify-rectangle' :identity ':::###::::XXXWWW1660034424===::' :close_action 
   './src/shell/combine.bash rmid 1660034424' :limit_body '110' :limit_summary '30' :summary 'Forbidden Silence' :body 'Raimu - Forbidden Silence' :close '繁' 
   :image_height 100 :image_width 100 :image '/home/maker/.cache/eww/dunst/image-data/Spotify-1660034424.png' :appname 'Spotify' :icon 
   '/home/maker/.cache/eww/dunst/image-data/Spotify-1660034424.png' :icon_height 32 :icon_width 32 :timestamp '14:10' :urgency 'LOW') (_cardimage 
   :class 'Spotify-rectangle' :identity ':::###::::XXXWWW1660034279===::' ...
   ```
 - <samp>combine.bash</samp>: Run this using `./logger.py init` which will initialize the [dbus](https://www.freedesktop.org/wiki/Software/dbus) eavesdropper. 
   Now, open another terminal and run `./combine.bash sub` then open another terminal and type `notfy-send hello`. Now, if something appears in the
   second terminal then the script is working. Sample should be the same as `logger.py`.
 - <samp>covidstate.py</samp>: This is currently not in use but you can test it regardless. Try running it `./covidstate.py` and see if there is any [JSON](https://www.json.org/json-en.html) output.
   You may need to wait for a few seconds by the way. Following is a sample.

   ```json
   {
     "country": {
     "India": {
       "id": "81",
       "country": "India",
       "confirmed": 44174650,
       "active": null,
       "deaths": 526772,
       "recovered": null,
   ...
   ```

 - <samp>github.sh</samp>: This too is not being used but wouldn't hurt to test it. Try running it by `./github.sh repos` see if there is any JSON output. And do the same for `./github.sh users` as well.
   Following is a sample.

   ```json
   [
     {
       "id": <some_number>,
       "node_id": <some_number>,
       "name": "dharmx",
       "full_name": "dharmx/dharmx",
       "private": false,
       "owner": {
         "login": "dharmx",
   ...
   ```
 - <samp>pollution.py</samp>: Do the same as `github.sh`.  Following is a sample.
   ```json
   {
     "coord": {
     "lon": 88.3832,
     "lat": 22.518
   },
   "list": [
     {
       "main": {
       "aqi": 3
     },
     "components": {
       "co": 487.33,
       "no": 0.13,
       "no2": 21.08,
       "o3": 39.34,
       "so2": 31.47,
       "pm2_5": 20.35,
       "pm10": 24.43,
       "nh3": 4.75
   ...
   ```
 - <samp>weather.py</samp>: Do the same as `github.sh` only difference is that you need to supply a flag i.e. `fetch`.
   Following is a sample.

   ```json
   {
     "coord": {
     "lon": 88.3832,
     "lat": 22.518
   },
   "weather": [
     {
       "id": 721,
       "main": "Haze",
       "description": "haze",
       "icon": "50d",
   ...
   ```
 - <samp>workspaces.zsh</samp>: This is [BSPWM](https://github.com/baskerville/bspwm) specific. Try running this by `./workspaces.zsh subscribe_desktop` then try going to any other workspace then return to the current one.
   Now, see if there are any JSON values. Following is a sample.

   ```json
   [
     {
       "class": "vertigo-button vertigo-workspace vertigo-workspace-occupied",
       "tooltip": "workspace:  state: occupied",
       "onclick": "bspc desktop --focus 1",
       "label": ""
     },
     {
       "class": "vertigo-button vertigo-workspace vertigo-workspace-local",
       "tooltip": "workspace:  state: local",
       "onclick": "bspc desktop --focus 2",
       "label": ""
     },
     {
       "class": "vertigo-button vertigo-workspace vertigo-workspace-focused",
       "tooltip": "workspace: 北 state: focused",
       "onclick": "bspc desktop --focus 3",
       "label": "北"
     }
   ]
   ```
 - <samp>mpdaemon.py</samp>: Same as `github.sh`. Also, you might need to 
   traverse through your current MPD music playlist and play some songs to be completely sure.
   While you are at it see if JSON output changes or, not as well. Sample as follows.

   ```json
   {
     "file": "/home/maker/.cache/eww/mpd/3PM Coding Session.png",
     "artist": "Lofi Ghostie",
     "albumartist": "Unknown",
     "title": "3PM Coding Session",
     "album": "Unknown",
     "last-modified": "2021-11-14T19:55:40Z",
     "format": "44100:24:2",
     "time": "4948",
     "duration": "4947.748",
     "pos": "0",
     "id": "1",
     "status": "pause",
     "bright": "#4959A5",
     "dark": "#CC96E0"
   }
   ```
 - <samp>playerctl.py</samp>: Similar to `mpdaemon.py`. Sample as follows.
   ```json
   {
     "mpris:artUrl": "/home/maker/.cache/eww/pctl/spotify/7468726565706F6F6C/4120506C6163652042656E65617468.png",
     "xesam:artist": "threepool",
     "xesam:title": "A Place Beneath",
     "xesam:album": "A Place Beneath",
     "status": "Playing",
     "mpris:trackid": "/com/spotify/track/4m1Kg8I715SQUSOjFrvxR7",
     "mpris:length": 132679000,
   ...
   ```
 - <samp>uptime.awk</samp>: Run this by `uptime --pretty | ./uptime.awk`. 
   Output should be `2d, 4h` for uptime of `up 2 days, 4 hours, 35 minutes`.

#### Caveats

If any of these do not work then consult the Troubleshooting, FAQ and Tips sections.

---

<div align="center">

# ⚠ UNDER CONSTRUCTION ⚠

<div>
