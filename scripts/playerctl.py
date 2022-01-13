#!/usr/bin/env python3.10

"""
This script that merely fetches track metadata.
"""

import sys
from os import getenv, listdir, mkdir, system
from os.path import isdir
from shutil import copyfileobj

from dbus import Interface, SessionBus
from dbus.exceptions import DBusException
from requests import get

playerctl_cache = getenv(
    "XDG_CACHE_HOME", f"{getenv('HOME')}/.cache") + "/playerctl-spt"


def get_metadata(properties):
    """Fetches spotify track metadata and encodes it into JSON format"""
    try:
        metadata = properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
        return {
            "message": "SUCCESS",
            "album": str(metadata["xesam:album"]),
            "title": str(metadata["xesam:title"]),
            "art": str(metadata["mpris:artUrl"]),
            "albumArtist": ", ".join((metadata["xesam:albumArtist"])),
            "artist": ", ".join((metadata["xesam:artist"])),
            "id": metadata["mpris:trackid"].split(sep=":")[-1],
        }
    except DBusException as exception:
        return {"exception": exception, "message": "ERROR"}


def cache_create() -> bool:
    """If the cache directory doesn't exist then create it"""
    if not isdir(playerctl_cache):
        mkdir(playerctl_cache)
        return False
    return True


def download_image(link: str, save_path: str):
    """Download an image to a specific path"""
    data = get(link, stream=True)
    if data.status_code == 200:
        data.raw.decode_content = True
        with open(save_path, "wb") as file:
            copyfileobj(data.raw, file)
    else:
        print("ERROR")


def save_cache(unique_name, link):
    """Downloads the image and writes the JSON track data to the subcache"""
    cache_create()
    save_path = f"{playerctl_cache}/{unique_name}"
    if not f"{unique_name}" in listdir(playerctl_cache):
        mkdir(save_path)
        download_image(link, f"{save_path}/art.jpg")
    return f"{save_path}/art.jpg"


def init():
    """Evaluates commandline arguments and outputs results accordingly"""
    args: list = sys.argv[1:]
    if not args:
        print("No option given!")
        return

    session_bus: SessionBus = SessionBus()

    try:
        player = session_bus.get_object(
            f"org.mpris.MediaPlayer2.{args[0]}", "/org/mpris/MediaPlayer2"
        )
        session_properties = Interface(
            player, "org.freedesktop.DBus.Properties")
        metadata: dict = get_metadata(session_properties)
        match args[1]:
            case "status":
                print(session_properties.Get(
                    'org.mpris.MediaPlayer2.Player', 'PlaybackStatus'))
            case "album":
                print(metadata["album"])
            case "title":
                print(metadata["title"])
            case "albumArtist":
                print(metadata["albumArtist"])
            case "artist":
                print(metadata["artist"])
            case "image":
                prepared = f"{metadata['artist']}-{metadata['album']}"
                print(save_cache(prepared, metadata["art"]))
            case "notify":
                prepared = f"{metadata['artist']}-{metadata['album']}"
                system(
                    "dunstify -a 'spotify' -i " + "'" +
                    save_cache(prepared, metadata['art']) + "'"
                    + " '" + metadata['title'] + "'" + " '" +
                    metadata['albumArtist'] + " - " + metadata['album']
                    + "'"
                )
            case "all":
                prepared = f"{metadata['artist']}-{metadata['album']}"
                metadata["save"] = save_cache(prepared, metadata['art'])
                print(metadata)
            case _:
                print("Invalid choice!")
    except DBusException:
        print("Offline")
    session_bus.close()


if __name__ == "__main__":
    init()

# vim:ft=python:nowrap
