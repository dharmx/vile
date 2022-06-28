#!/usr/bin/env --split-string=python -u

import json
import os
import pathlib
import shutil
import subprocess

import gi
gi.require_version("Playerctl", "2.0")
from gi.repository import GLib, Playerctl
import requests


def on_metadata(*args):
    # sourcery skip: identity-comprehension, remove-redundant-constructor-in-dict-union
    metadata = {
        "mpris:artUrl": default_cover,
        "xesam:artist": "Unknown",
        "xesam:title": "Unknown",
        "xesam:album": "Unknown",
        "status": "Stopped",
    } | {key: val for key, val in dict(args[1]).items() if val}
    name = args[0].props.player_name
    metadata["player"] = name or "none"
    metadata["status"] = args[0].props.status

    if not "".join(metadata["xesam:artist"]):
        metadata["xesam:artist"] = "Unknown"
    elif len(metadata["xesam:artist"]) == 1:
        metadata["xesam:artist"] = metadata["xesam:artist"][0]
    elif len(metadata["xesam:artist"]) == 2:
        metadata["xesam:artist"] = "and".join(metadata["xesam:artist"])
    else:
        metadata["xesam:artist"] = "and".join(
            [",".join(metadata["xesam:artist"][:-1]), metadata["xesam:artist"][-1]]
        )
    if (
        "file://" not in metadata["mpris:artUrl"]
        and default_cover not in metadata["mpris:artUrl"]
    ):
        metadata["mpris:artUrl"] = cache_and_get(metadata)
    metadata |= get_bright_dark_from_cover(metadata["mpris:artUrl"])
    print(json.dumps(metadata))


on_play_pause = lambda player, *_: on_metadata(player, player.props.metadata)


def init_player(name):
    player = Playerctl.Player.new_from_name(name)
    player.connect("metadata", on_metadata, manager)
    player.connect("playback-status::playing", on_play_pause, manager)
    player.connect("playback-status::paused", on_play_pause, manager)
    manager.manage_player(player)


def player_null_check(player_manager):
    if not len(player_manager.props.player_names):
        metadata =  {
            "mpris:artUrl": default_cover,
            "xesam:artist": "Unavailable",
            "xesam:title": "Unavailable",
            "xesam:album": "Unavailable",
            "status": "Stopped",
            "player": "none",
        }
        metadata |= get_bright_dark_from_cover(default_cover)
        print(json.dumps(metadata))
        return False
    return True


def on_name_appeared_vanished(player_manager, name):
    if player_null_check(player_manager):
        init_player(name)


def gen_hex_path_encode(unique_path_name: list):
    return "".join(["%X" % ord(char) for char in unique_path_name])


def fetch_save_cover(link, save_path):
    data = requests.get(link, stream=True)
    if data.status_code == 200:
        data.raw.decode_content = True
        with open(save_path, "wb") as file:
            shutil.copyfileobj(data.raw, file)
        return True
    return False


def cache_and_get(metadata):
    player_dir = f"{pctl_cache}/{metadata['player']}"
    if metadata["player"] not in ["none", "firefox"]:
        new_meta = {
            "artist": gen_hex_path_encode(metadata["xesam:artist"]),
            "album": gen_hex_path_encode(metadata["xesam:album"]),
            "title": gen_hex_path_encode(metadata["xesam:title"]),
        }
        gen_path = f"{player_dir}/{new_meta['artist']}"
        if not os.path.isdir(gen_path):
            pathlib.Path(gen_path).mkdir(parents=True, exist_ok=True)

        cover_path = f"{gen_path}/{new_meta['album']}.png"
        if not os.path.exists(cover_path):
            try:
                return (
                    cover_path
                    if fetch_save_cover(metadata["mpris:artUrl"], cover_path)
                    else default_cover
                )
            except requests.exceptions.ConnectionError:
                return default_cover
        return cover_path
    return default_cover


def get_bright_dark_from_cover(image_path) -> dict:
    if image_path == default_cover:
        return {'bright': '#292929', 'dark': '#BEBFC1'}
    colors = [
        *map(
            lambda item: item.strip().split(" ")[2][:7],
            (
                subprocess.check_output(
                    " ".join(
                        [
                            "convert",
                            f'"{image_path}"',
                            "-depth",
                            "8",
                            "+dither",
                            "-colors",
                            "8",
                            "-format",
                            "%c",
                            "histogram:info:",
                        ]
                    ),
                    shell=True,
                )
                .decode("utf8")
                .splitlines()
            ),
        )
    ]

    return {"bright": colors[0], "dark": colors[5]}


if __name__ == "__main__":
    with open("./.config.json", encoding="utf8") as file:
        config: dict = json.loads(file.read())["player"]
        default_cover = os.path.expandvars(config["default_art"])
        pctl_cache = os.path.expandvars(config["pctl_cache"])

    manager = Playerctl.PlayerManager()
    manager.connect("name-appeared", on_name_appeared_vanished)
    manager.connect("name-vanished", on_name_appeared_vanished)

    [init_player(name) for name in manager.props.player_names]
    if player_null_check(manager):
        player = Playerctl.Player()
        on_metadata(player, player.props.metadata)

    GLib.MainLoop().run()

# vim:filetype=python
