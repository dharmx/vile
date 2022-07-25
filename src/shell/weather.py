#!/usr/bin/env python

import json
import os
import pathlib
import sys
from datetime import datetime

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


def check_cache_and_get(cache: str, fallback: str, token: str, icon_dir: str) -> str:
    now = datetime.now()
    date_path = pathlib.PosixPath(f"{cache}/weather-{now.strftime('%F')}.json")

    if now.hour > 15 and now.hour < 5:
        date_path.unlink(date_path)
    prepared_link = prepare_link(config["weather"], token)

    if not date_path.is_file() and not fetch_save_str(prepared_link, str(date_path)):
        fallback_metadata = json.loads(pathlib.PosixPath(fallback).read_text())
        return overwrite_weather_icon_timed(fallback_metadata, icon_dir)
    return overwrite_weather_icon_timed(json.loads(date_path.read_text()), icon_dir)


def overwrite_weather_icon_timed(metadata: dict, icon_dir: str) -> dict:
    now = datetime.now()
    if now.hour > 4 and now.hour < 16:
        metadata["weather"][0]["icon"] = (
            f"{icon_dir}/{metadata['weather'][0]['icon'].replace('n', 'd')}.png"
            if 'n' in metadata['weather'][0]['icon']
            else f"{icon_dir}/{metadata['weather'][0]['icon']}.png")
    elif 'd' in metadata['weather'][0]['icon']:
        metadata["weather"][0]["icon"] = \
            f"{icon_dir}/{metadata['weather'][0]['icon'].replace('d', 'n')}.png"
    else:
        metadata["weather"][0]["icon"] = f"{icon_dir}/{metadata['weather'][0]['icon']}.png"
    return metadata


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
    config["weather"]["icon_dir"] = os.path.expandvars(
        config["weather"]["icon_dir"])
    pathlib.PosixPath(config["weather"]["cache_dir"]).mkdir(
        parents=True, exist_ok=True)

    match sys.argv[1]:
        case "fetch":
            _metadata = json.loads(
                pathlib.PosixPath(FALLBACK_PATH).read_text())
            _metadata = overwrite_weather_icon_timed(
                _metadata, config["weather"]["icon_dir"])
            print(json.dumps(_metadata))  # fallback print

            _metadata = check_cache_and_get(
                config["weather"]["cache_dir"],
                FALLBACK_PATH,
                config["tokens"]["openweather"],
                config["weather"]["icon_dir"],
            )
            print(json.dumps(_metadata))
        case "link":
            print(prepare_link(config["weather"],
                  config["tokens"]["openweather"]))

# vim:filetype=python
