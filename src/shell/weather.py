#!/usr/bin/env python

import json
import os
import pathlib
import sys
from datetime import datetime

import requests

import utils

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


def fetch_save(link: str, save_path: str) -> bool:
    try:
        data = requests.get(link)
        if data.status_code == 200:
            metadata = data.json()
            metadata["weather"][0]["glyph"] = assign_glyph(metadata["weather"][0]["icon"])
            pathlib.PosixPath(save_path).write_text(json.dumps(metadata))
            return True
        return False
    except requests.exceptions.ConnectionError:
        return False


# Depends on phosphor
def assign_glyph(icon_name: str) -> str:
    match icon_name[:-1]:
        case "01":
            icon_name = ""
        case "02":
            icon_name = ""
        case "03":
            icon_name = ""
        case "04":
            icon_name = ""
        case "09":
            icon_name = ""
        case "10":
            icon_name = ""
        case "11":
            icon_name = ""
        case "13":
            icon_name = ""
        case "50":
            icon_name = ""
        case _:
            icon_name = ""
    return icon_name


def day_night(path_frag: str, time_of_day: str, date_time: datetime) -> pathlib.PosixPath:
    return pathlib.PosixPath(f"{path_frag}/weather-{date_time.strftime('%F')}-{time_of_day}.json")


def cache_and_get(cache: str, fallback: str, token: str) -> pathlib.PosixPath:
    now = datetime.now()
    date_path = day_night(cache, "day", now)
    if now.hour > 15 or now.hour < 4:
        date_path = day_night(cache, "night", now)

    if config["weather"]["method"] == "automatic":
        config["weather"] |= auto_locate(config["weather"]["cache_dir"])
    prepared_link = prepare_link(config["weather"], token)

    if not date_path.is_file() and not fetch_save(prepared_link, str(date_path)):
        return json.loads(pathlib.PosixPath(fallback).read_text())
    return json.loads(date_path.read_text())


def auto_locate(cache_dir: str) -> dict:
    cache_posix_path = pathlib.PosixPath(f"{cache_dir}/location.json")
    if not cache_posix_path.is_file(): # assuming the directory exists
        fetched_location = utils.get_location()
        cache_posix_path.write_text(json.dumps(fetched_location))
        return fetched_location
    return json.loads(cache_posix_path.read_text())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("No such option!")

    # NOTE: Change these only if you know what you are doing.
    CONFIG_PATH = os.path.expandvars("$XDG_CONFIG_HOME/eww/.config.json")
    FALLBACK_PATH = os.path.expandvars(
        "$XDG_CONFIG_HOME/eww/assets/fallback.json")
    config = json.loads(pathlib.PosixPath(CONFIG_PATH).read_text())

    config["weather"]["cache_dir"] = os.path.expandvars(
        config["weather"]["cache_dir"])
    pathlib.PosixPath(config["weather"]["cache_dir"]).mkdir(
        parents=True, exist_ok=True)

    match sys.argv[1]:
        case "fetch":
            _metadata = cache_and_get(
                config["weather"]["cache_dir"],
                FALLBACK_PATH,
                config["tokens"]["openweather"],
            )
            print(json.dumps(_metadata))


# vim:filetype=python
