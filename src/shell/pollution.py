#!/usr/bin/env python

from datetime import datetime
import utils
import json
import os
import pathlib


def prepare_link(options: dict, token: str) -> str | None:
    link = f"http://api.openweathermap.org/data/2.5/air_pollution?appid={token}"
    link_fragment = ""
    if options["latitude"] and options["longitude"]:
        link_fragment += f"&lat={options['latitude']}&lon={options['longitude']}"
    return f"{link}{link_fragment}" if link_fragment else None


def cache_pollution_get(config: dict) -> dict:
    location = None
    if config["location"]["method"] == "automatic":
        location = utils.auto_locate(config["location"]["cache_dir"])
    elif config["location"]["method"] == "manual":
        location = config["location"]
    else:
        print("Unknown Method!")
        exit(1)
    token = config["tokens"]["openweather"]
    prepared_link = prepare_link(location, token)
    cache_path = pathlib.PosixPath(f"{config['pollution']['cache_dir']}/pollution-{datetime.now().strftime('%F')}.json")
    if not cache_path.is_file():
        def callback(metadata: dict) -> dict:
            metadata["icons"] = config["pollution"]["icons"]
            return metadata
        utils.fetch_save(prepared_link, str(cache_path), callback)
    return cache_path.read_text()


if __name__ == "__main__":
    CONFIG = json.loads(pathlib.PosixPath(os.path.expandvars("$XDG_CONFIG_HOME/eww/ewwrc")).read_text())
    CONFIG["pollution"]["cache_dir"] = os.path.expandvars(CONFIG["pollution"]["cache_dir"])
    CONFIG["location"]["cache_dir"] = os.path.expandvars(CONFIG["location"]["cache_dir"])
    pathlib.PosixPath(CONFIG["pollution"]["cache_dir"]).mkdir(parents=True, exist_ok=True)
    print(cache_pollution_get(CONFIG))


# vim:filetype=python
