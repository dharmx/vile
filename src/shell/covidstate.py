#!/usr/bin/env python

import json
import os
import pathlib
from datetime import datetime

import covid
import requests
import utils

_config = json.loads(pathlib.PosixPath(os.path.expandvars("$XDG_CONFIG_HOME/eww/ewwrc")).read_text())
_config["covid"]["cache_dir"] = os.path.expandvars(_config["covid"]["cache_dir"])
_config["location"]["cache_dir"] = os.path.expandvars(_config["location"]["cache_dir"])

pathlib.PosixPath(_config["location"]["cache_dir"]).mkdir(parents=True, exist_ok=True)
_cache_posix = pathlib.PosixPath(_config["covid"]["cache_dir"])
if not _cache_posix.is_dir():
    _cache_posix.mkdir(parents=True, exist_ok=True)

_covid = covid.Covid()
_fallback = {
    "country": "NA",
    "confirmed": "NA",
    "deaths": "NA",
    "icons": _config["covid"]["icons"]
}

if _config["location"]["method"] == "automatic":
    _country = utils.auto_locate(_config["location"]["cache_dir"])
    if not _country:
        print(_fallback)
        exit(0)
elif _config["location"]["method"] == "manual":
    _country = _config["covid"]["country"]
else:
    print("Unknown Value!")
    exit(1)

try:
    _now = datetime.now().strftime("%F")
    _path_format = pathlib.PosixPath(f"{_config['covid']['cache_dir']}/covid-{_now}.json")
    if not _path_format.is_file():
        data = _fallback | {
            "country": {
                _country["country"]: _covid.get_status_by_country_name(_country["country"].lower())
            },
            "confirmed": _covid.get_total_confirmed_cases(),
            "deaths": _covid.get_total_deaths(),
        }
        data = json.dumps(data)
        _path_format.write_text(data)
    print(_path_format.read_text())
except requests.exceptions.ConnectionError:
    print(_fallback)

# vim:filetype=python
