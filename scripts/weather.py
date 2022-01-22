#!/usr/bin/env python3.10
"""
Uses OpenWeather API
"""

import sys
from datetime import datetime
from json import dumps, loads
from os import getenv, listdir, mkdir, system
from os.path import isdir

from dotenv import load_dotenv
from requests import get

xdg_config: str = getenv("XDG_CONFIG_HOME")
xdg_cache: str = getenv("XDG_CACHE_HOME")

date: str = datetime.today().strftime("%Y-%m-%d")
cache: str = f"{xdg_cache}/weather"


def cachedirexists() -> None:
    """Checks for the cache weather directory"""
    if not isdir(cache):
        mkdir(cache)
        system(
            f"ln -s {xdg_config}/eww/structs/side-utils/weather/weather-icons {cache}"
        )


def checkrecord(cachedate: str = date) -> bool:
    """Checks if today's weather has already been cached"""
    if f"weather-{cachedate}.json" in listdir(f"{cache}"):
        return True
    return False


def validatecache(cachedate: str = date) -> bool:
    """Sees if the specific cache is valid or, has been rate-limited"""
    if not f"weather-{cachedate}.json" in listdir(f"{cache}"):
        return False
    with open(f"{cache}/weather-{cachedate}.json", encoding="utf-8") as file:
        if '"message"' in file.read():
            return False
        return True


def preparelink() -> str:
    """Prepare the weather API link"""
    load_dotenv(
        f"{xdg_config}/eww/structs/side-utils/.weather-env")
    city: str = getenv("CITY")
    token: str = getenv("TOKEN")
    return f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={token}"


def cacheweather(prepared: str) -> None:
    """Fetches and saves weather info to cache in the form of JSON"""
    weather_json: str = loads(get(prepared).text)
    with open(f"{cache}/weather-{date}.json", "w", encoding="utf-8") as file:
        file.write(dumps(weather_json, sort_keys=True, indent=4))


def init() -> None:
    """Driver function"""
    args: list = sys.argv[1:]

    if not args:
        print("No option given!")
        return

    match args[0]:
        case "today":
            match args[1]:
                case "fetch":
                    if not validatecache(date):
                        cacheweather(preparelink())
                case "icon-link":
                    if not validatecache(date):
                        print(f"{xdg_config}/eww/assets/images/cloud.svg")
                    else:
                        with open(f"{cache}/weather-{date}.json", encoding="utf-8") as file:
                            loadedjson: dict = loads(file.read())
                            print(
                                "https://openweathermap.org/img/wn/" +
                                f"{loadedjson['weather'][0]['icon']}@2x.png"
                            )
                case "icon":
                    if not validatecache(date):
                        print(f"{xdg_config}/eww/assets/images/cloud.svg")
                    else:
                        with open(f"{cache}/weather-{date}.json", encoding="utf-8") as file:
                            loadedjson: dict = loads(file.read())
                            print(
                                xdg_config +
                                "/eww/structs/side-utils/weather/weather-icons/" +
                                loadedjson['weather'][0]['icon'] +
                                "@2x.png"
                            )
                case "temp":
                    with open(f"{cache}/weather-{date}.json", encoding="utf-8") as file:
                        loadedjson: dict = loads(file.read())
                        if len(args) == 3 and args[2] == "unit":
                            print(f'{int(loadedjson["main"]["temp"])}°C')
                        else:
                            print(int(loadedjson["main"]["temp"]))
                case "type":
                    with open(f"{cache}/weather-{date}.json", encoding="utf-8") as file:
                        loadedjson: dict = loads(file.read())
                        print(loadedjson["weather"][0]["main"])
                case "city":
                    with open(f"{cache}/weather-{date}.json", encoding="utf-8") as file:
                        loadedjson: dict = loads(file.read())
                        print(loadedjson["name"])
                case "json":
                    with open(f"{cache}/weather-{date}.json", encoding="utf-8") as file:
                        print(loads(file.read()))
                case "feels":
                    with open(f"{cache}/weather-{date}.json", encoding="utf-8") as file:
                        loadedjson: dict = loads(file.read())
                        print(int(loadedjson["main"]["feels_like"]))
                case "max":
                    with open(f"{cache}/weather-{date}.json", encoding="utf-8") as file:
                        loadedjson: dict = loads(file.read())
                        print(int(loadedjson["main"]["temp_max"]))
                case "min":
                    with open(f"{cache}/weather-{date}.json", encoding="utf-8") as file:
                        loadedjson: dict = loads(file.read())
                        print(int(loadedjson["main"]["temp_min"]))
                case _:
                    print("Invalid Option!")
        case _:
            print("Invalid Option!")


if __name__ == "__main__":
    cachedirexists()
    try:
        init()
    except FileNotFoundError as file_not_found_error:
        print("Offline")

# vim:ft=python:nowrap
