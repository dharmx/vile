#!/usr/bin/env zsh

## Copyright (C) 2020-2022 Aditya Shakya <adi1090x@gmail.com>
## Everyone is permitted to copy and distribute copies of this file under GNU-GPL3

DIR="$HOME/.config/berry"
rofi_command="rofi -theme $DIR/rofi/themes/screenshot.rasi"

time=`date +%Y-%m-%d-%H-%M-%S`
geometry=`xrandr | head -n1 | cut -d',' -f2 | tr -d '[:blank:],current'`
dir="`xdg-user-dir PICTURES`/Screenshots"
file="Screenshot_${time}_${geometry}.png"

# Buttons
screen=""
area=""
window=""
infive=""
inten=""

# notify and view screenshot
notify_view () {
	dunstify -u low --replace=699 -i /usr/share/archcraft/icons/dunst/picture.png "Copied to clipboard."
	viewnior ${dir}/"$file"
	if [[ -e "$dir/$file" ]]; then
		dunstify -u low --replace=699 -i /usr/share/archcraft/icons/dunst/picture.png "Screenshot Saved."
	else
		dunstify -u low --replace=699 -i /usr/share/archcraft/icons/dunst/picture.png "Screenshot Deleted."
	fi
}

# countdown
countdown () {
	for sec in `seq $1 -1 1`; do
		dunstify -t 1000 --replace=699 -i /usr/share/archcraft/icons/dunst/timer.png "Taking shot in : $sec"
		sleep 1
	done
}

# take shots
shotnow () {
	cd ${dir} && sleep 0.5 && maim -u -f png | tee "$file" | xclip -selection clipboard -t image/png
	notify_view
}

shot5 () {
	countdown '5'
	sleep 1 && cd ${dir} && maim -u -f png | tee "$file" | xclip -selection clipboard -t image/png
	notify_view
}

shot10 () {
	countdown '10'
	sleep 1 && cd ${dir} && maim -u -f png | tee "$file" | xclip -selection clipboard -t image/png
	notify_view
}

shotwin () {
	cd ${dir} && maim -u -f png -i `xdotool getactivewindow` | tee "$file" | xclip -selection clipboard -t image/png
	notify_view
}

shotarea () {
	cd ${dir} && maim -u -f png -s -b 2 -c 0.35,0.55,0.85,0.25 -l | tee "$file" | xclip -selection clipboard -t image/png
	notify_view
}

if [[ ! -d "$dir" ]]; then
	mkdir -p "$dir"
fi

# Variable passed to rofi
options="$screen\n$area\n$window\n$infive\n$inten"

chosen="$(echo -e "$options" | $rofi_command -p 'Take Screenshot' -dmenu -selected-row 0)"
case $chosen in
    $screen)
		shotnow
        ;;
    $area)
		shotarea
        ;;
    $window)
		shotwin
		;;
    $infive)
		shot5
		;;
    $inten)
		shot10
        ;;
esac

