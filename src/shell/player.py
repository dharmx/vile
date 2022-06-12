#!/usr/bin/env --split-string=python -u

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time

import gi
import mpd
from mpd.base import CommandError

gi.require_version("Playerctl", "2.0")
from gi.repository import GLib, Playerctl

with open("./.config.json", encoding="utf8") as file:
    config: dict = json.loads(file.read())["player"]
    config["default_art"] = os.path.expandvars(config["default_art"])
    config["mpd_cache"] = os.path.expandvars(config["mpd_cache"])
    config["pctl_cache"] = os.path.expandvars(config["pctl_cache"])


class MPDHandler:
    def __init__(self, prefix, cache, default) -> None:
        """Setup MPD client for use."""
        self._client: mpd.MPDClient = mpd.MPDClient()
        self._client.timeout = 3
        self._client.connect("localhost", 6600)

        # equivalent: mkdir --parents
        self.prefix, self.cache, self.default = prefix, cache, default
        pathlib.Path(self.prefix).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.cache).mkdir(parents=True, exist_ok=True)

    def _validatepath(self, path: str) -> str:
        path = os.path.dirname(path)
        return f"{path}/" if "/" in path or path else path

    def _embeddedcover(self, key: str) -> str or bytes:
        content = self._client.readpicture(key)
        if not content:
            try:
                content = self._client.albumart(key)
            except CommandError:
                content = {"binary": self.default}
        return content["binary"]

    def get(self, key: str) -> str:
        music: str = (
            f"{self.cache}/{self._validatepath(key)}{pathlib.Path(key).stem}.png"
        )
        return music if os.path.exists(music) else self.default

    def create(self, key: str) -> bool:
        # a/b/c/d.e: dirname -> a/b/c | stem -> d
        # generate cache path -> cache + dirname + stem + ".png"
        cachefull = f"{self._validatepath(key)}{pathlib.Path(key).stem}"
        if not os.path.exists(f"{self.cache}/{cachefull}.png"):
            if covercontent := self._embeddedcover(f"{cachefull}.mp3"):
                if type(covercontent) != str:  # check
                    pathlib.Path(os.path.dirname(f"{self.cache}/{key}")).mkdir(
                        parents=True, exist_ok=True
                    )
                    with open(f"{self.cache}/{cachefull}.png", "wb") as target:
                        target.write(covercontent)  # then write bytes to file
                return True
            return False
        return False  # will return True iff a file is created

    def toggle(self, function) -> bool:
        currentstatus = json.loads(self.metadatajson())
        functions: dict = {
            "consume": self._client.consume,
            "single": self._client.single,
            "random": self._client.random,
            "repeat": self._client.repeat,
            "shuffle": self._client.shuffle,
        }
        function in functions and functions[function]
        (0 if currentstatus[function] == "1" else 1)

    def playback(self, function) -> None:
        functions: dict = {
            "play": self._client.play,
            "pause": self._client.pause,
            "stop": self._client.stop,
            "prev": self._client.previous,
            "next": self._client.next,
            "toggle": lambda: self._client.pause()
            if self.metadatajson(tojson=False)["state"] == "play"
            else self._client.play(),
        }
        try:
            function in functions and functions[function]()
        except CommandError:
            print("Unsupported function.")

    def metadatajson(self, tojson=True) -> str or dict:
        metadata: dict = self._client.status()
        metadata["current"] = {
            "file": config["default_art"],
            "artist": "Unknown",
            "albumartist": "Unknown",
            "title": "Unknown",
            "album": "Unknown",
        }
        metadata["current"] |= self._client.currentsong()
        metadata["stats"] = self._client.stats()
        metadata["current"]["file"] = self.get(metadata["current"]["file"])

        colors = [
            *map(
                lambda item: item.strip().split(" ")[2][:7],
                (
                    subprocess.check_output(
                        " ".join(
                            [
                                "convert",
                                f"\"{metadata['current']['file']}\"",
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
                        shell=True
                    )
                    .decode("utf8")
                    .splitlines()
                ),
            )
        ]

        metadata["current"]["bright"] = colors[0]
        metadata["current"]["dark"] = colors[5]
        return json.dumps(metadata) if tojson else metadata

    def statusmon(self) -> None:
        old = self._client.status()["state"]
        print(old)
        while not time.sleep(0.3):
            new = self._client.status()["state"]
            if new != old:
                print(new)
                old = new

    def cacheplaylist(self) -> None:
        [self.create(file[6:]) for file in self._client.playlist()]

    def cachedatatbase(self) -> None:
        self._client.rescan()
        self._client.update()
        for file in self._client.listall():
            todict: dict = dict(file)
            if "directory" not in todict:
                self.create(todict["file"])

    def subscribe(self, interval: float = 1.0) -> str:
        old = self.metadatajson(tojson=False)["current"]
        print(json.dumps(old))
        while not time.sleep(interval):
            new = self.metadatajson(tojson=False)["current"]
            old_formatted = f"{old['artist']}-{old['title']}-{old['album']}"
            new_formatted = f"{new['artist']}-{new['title']}-{new['album']}"
            if old_formatted != new_formatted:
                print(json.dumps(new))
                old = new

    def close(self) -> None:
        self._client.close()
        self._client.disconnect()


# loop_status metadata playback_status
# player_instance player_name
class PCTLHandler:
    def __init__(self, cache: str, default: str) -> None:
        self.cache = cache
        self.default = default
        pathlib.Path(self.cache).mkdir(parents=True, exist_ok=True)

    def playback(self, player, function) -> None:
        supports = player.props
        functions = {
            "play": lambda: supports.can_play and player.play(),
            "pause": lambda: supports.can_pause and player.pause(),
            "stop": lambda: supports.can_pause and player.stop(),
            "prev": lambda: supports.can_go_previous and player.previous(),
            "next": lambda: supports.can_go_next and player.next(),
            "toggle": lambda: supports.can_play
            and supports.can_pause
            and player.play_pause(),
        }
        function in functions and functions[function]()

    def metadatajson(self, player, tojson=True) -> str or dict:
        metadata: dict = {
            "mpris:artUrl": self.default,
            "xesam:artist": "Unknown",
            "xesam:title": "Unknown",
            "xesam:album": "Unknown",
            "mpris:trackid": "none",
            "player": "none",
        }

        metadata |= {
            key: value for key, value in dict(player.props.metadata).items() if value
        }

        metadata["player"] = player.props.player_name
        if metadata["xesam:artist"] and type(metadata["xesam:artist"]) == list:
            metadata["xesam:artist"] = ", ".join(metadata["xesam:artist"])
        return json.dumps(metadata) if tojson else metadata

    def subscribe(self) -> None:
        print(self.metadatajson(Playerctl.Player()))
        manager = Playerctl.PlayerManager()

        def onmetadata(player, *_):
            print(self.metadatajson(player))

        def initplayer(name) -> None:
            player = None
            if type(name) == Playerctl.Player:
                player = name
            else:
                player = Playerctl.Player.new_from_name(name)
            player.connect("metadata", onmetadata, manager)
            manager.manage_player(player)

        manager.connect("name-appeared", lambda _, name: initplayer(name))
        manager.connect("player-vanished", lambda _, player: initplayer(player))

        [initplayer(name) for name in manager.props.player_names]
        GLib.MainLoop().run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        usage="%(prog)s [INTERFACE] [OPTIONS] [FLAGS]",
        description="CLI tool for managing mpd and playerctl metadata.",
    )

    parser.add_argument(
        "-I",
        "--interface",
        required=True,
        choices=["mpd", "pctl"],
        help="manage a supported player metadata",
    )

    parser.add_argument(
        "-j", "--json", action="store_true", help="get metadata in json format"
    )

    parser.add_argument(
        "-s",
        "--subscribe",
        type=float,
        help="print json metadata when a song changes",
    )

    parser.add_argument(
        "-p",
        "--playback",
        type=str,
        help="control player state like play / pause / next",
        choices=["next", "prev", "stop", "toggle", "play", "pause"],
    )

    args: argparse.Namespace = parser.parse_args(sys.argv[1:])

    match args.interface:
        case "mpd":
            handler = MPDHandler(
                os.path.expandvars("$XDG_MUSIC_DIR"),
                config["mpd_cache"],
                config["default_art"],
            )
            if args.json:
                print(handler.metadatajson())
            elif args.subscribe:
                if args.subscribe > 0:
                    handler.subscribe(args.subscribe)
                elif args.subscribe < 0:
                    handler.statusmon()
                else:
                    handler.subscribe()
            if args.playback:
                handler.playback(args.playback)
            handler.close()
        case "pctl":
            handler = PCTLHandler(config["pctl_cache"], config["default_art"])
            player = Playerctl.Player()
            if args.json:
                print(handler.metadatajson(player))
            elif args.playback:
                handler.playback(player, args.playback)
            elif args.subscribe:
                handler.subscribe()
            elif args.subscribe < 0:
                print("arg of -s/--subscribe must be greater than 0")

# vim:filetype=python
