#!/usr/bin/env python

from datetime import datetime
import json
import pathlib
import sys
import os
import requests


def prepare_link(options: dict, token: str) -> str | None:
    link = f"https://api.openweathermap.org/data/2.5/weather?appid={token}"
    link_fragment = ""

    if options["latitude"] and options["longitude"]:
        # always give priority to lat and long
        link_fragment += f"&lat={options['latitude']}&lon={options['longitude']}"
    else:
        if options["city"]:
            link_fragment += f"&q={options['city']}"
        if not options["country_code"]:
            return
        if options["zip"] and not options["city"]:
            link_fragment += f"&zip={options['zip']}"
        link_fragment += f",{options['country_code']}"

    if options["lang"]:
        # https://openweathermap.org/current#multi
        link_fragment += f"&lang={options['lang']}"

    if options["units"]:
        # standard, metric, imperial
        link_fragment += f"&units={options['units']}"

    return f"{link}{link_fragment}" if link_fragment else None


def fetch_save_str(link: str, save_path: str) -> bool:
    data = requests.get(link)
    if data.status_code == 200:
        pathlib.PosixPath(save_path).write_text(data.text)
        return True
    return False


def check_cache_and_get(cache: str, fallback: str) -> str:
    date_path = pathlib.PosixPath(f"{cache}/weather-{datetime.now().strftime('%F')}.json")
    prepared_link = prepare_link(config["weather"])
    if not date_path.is_file() and not fetch_save_str(prepared_link, date_path):
        return fallback
    return str(date_path)


def overwrite_weather_icon(icon_link: str) -> str:
    pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("No such option!")

    # NOTE: Change this only if you know what you are doing.
    CONFIG_PATH = os.path.expandvars("$XDG_CONFIG_HOME/eww/.config.json")
    FALLBACK_PATH = os.path.expandvars("$XDG_CONFIG_HOME/eww/assets/fallback.json")
    config = json.loads(pathlib.PosixPath(CONFIG_PATH).read_text())

    config["weather"]["cache_dir"] = os.path.expandvars(config["weather"]["cache_dir"])
    pathlib.PosixPath(config["weather"]["cache_dir"]).mkdir(parents=True, exist_ok=True)

    match sys.argv[1]:
        case "fetch":
            pass

# vim:filetype=python
