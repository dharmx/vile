import argparse
import json
import os
import pathlib
import sys
import time
import socket

import dbus
import mpd
from dbus.exceptions import DBusException
from mpd.base import CommandError

with open("../.config.json", encoding="utf8") as file:
    config: dict = json.loads(file.read())["player"]
    config["default_art"] = os.path.expandvars(config["default_art"])


class MPDHandler:
    def __init__(self, prefix, cache, default) -> None:
        """Setup MPD client for use."""
        self.fetch = 0
        self._client: mpd.MPDClient = mpd.MPDClient()
        self._client.timeout = 3
        self._client.connect("localhost", 6600)

        # equivalent: mkdir --parents
        self.prefix, self.cache, self.default = (
            os.path.expandvars(path) for path in (prefix, cache, default)
        )
        pathlib.Path(self.prefix).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.cache).mkdir(parents=True, exist_ok=True)

    def _validatepath(path: str) -> str:
        path = os.path.dirname(path)
        return path + "/" if "/" in path or path else path

    def _embeddedcover(self, key: str) -> None or bytes:
        content = self._client.readpicture(key)
        if not content:
            try:
                content = self._client.albumart(key)
            except CommandError:
                content = {"binary": open(self.default, "rb").read()}
        return content["binary"]

    def get(self, key: str) -> str:
        music: str = f"{self.cache}/{os.path.dirname(key)}/{pathlib.Path(key).stem}.png"
        return music if os.path.exists(music) else self.default

    def create(self, key: str) -> bool:
        # a/b/c/d.e: dirname -> a/b/c | stem -> d
        # generate cache path -> cache + dirname + stem + ".png"
        pathlib.Path(os.path.dirname(f"{self.cache}/{key}")).mkdir(
            parents=True, exist_ok=True
        )
        cachefull = f"{MPDHandler._validatepath(key)}{pathlib.Path(key).stem}"

        if not os.path.exists(f"{self.cache}/{cachefull}.png"):
            # try fetch the embedded cover in the mp3 file
            covercontent = self._embeddedcover(f"{cachefull}.mp3")

            if covercontent:  # check if mp3 has cover art
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
        function in functions and functions[function](
            0 if currentstatus[function] == "1" else 1
        )

    def playback(self, function) -> None:
        functions: dict = {
            "play": self._client.play,
            "pause": self._client.pause,
            "stop": self._client.stop,
            "previous": self._client.previous,
            "toggle": lambda: self._client.pause()
            if self.metadatajson(True)["state"] == "play"
            else self._client.play(),
        }
        function in functions and functions[function]()

    def metadatajson(self, tojson=True) -> str or dict:
        metadata: dict = self._client.status()
        metadata["current"] = self._client.currentsong()
        metadata["stats"] = self._client.stats()
        metadata["cachepath"] = (
            self.get(metadata["current"]["file"]) if metadata["current"] else {}
        )
        return metadata if not tojson else json.dumps(metadata)

    def cacheplaylist(self) -> None:
        [self.create(file[6:]) for file in self._client.playlist()]

    def cachedatatbase(self) -> None:
        self._client.rescan()
        self._client.update()
        for file in self._client.listall():
            todict: dict = dict(file)
            if not "directory" in todict:
                self.create(todict["file"])

    def subscribe(self, interval: float = 1.0) -> str:
        while not time.sleep(interval):
            print(self.metadatajson())

    def close(self) -> None:
        self._client.close()
        self._client.disconnect()


class PCTLHandler:
    def __init__(self, cache: str) -> None:
        self.cache = os.path.expandvars(cache)
        pathlib.Path(self.cache).mkdir(parents=True, exist_ok=True)

        self._bus = dbus.SessionBus()
        self._player = self._bus.get_object(
            "org.mpris.MediaPlayer2.playerctld", "/org/mpris/MediaPlayer2"
        )

    def _connected():
        try:
            sock = socket.create_connection(("www.google.com", 80))
            not sock and sock.close()
            return True
        except OSError:
            pass
        return False

    def metadatajson(self, tojson=True) -> str or dict:
        metadata = {
            "xesam:title": "Unknown",
            "xesam:album": "Unknown",
            "xesam:artist": "Unknown",
            "xesam:artUrl": config["default_art"],
            "xesam:trackid": "Unknown",
        }
        try:
            # INFO: https://amish.naidu.dev/blog/dbus
            properties = dbus.Interface(self._player, "org.freedesktop.DBus.Properties")
            metadata = metadata | properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
        except DBusException:
            pass
        return json.loads(json.dumps(metadata)) if not tojson else json.dumps(metadata)

    def playback(self, function: str) -> None:
        interface = dbus.Interface(
            self._player, dbus_interface="org.mpris.MediaPlayer2.Player"
        )
        functions: dict = {
            "play": interface.Next,
            "pause": interface.Pause,
            "toggle": interface.PlayPause,
            "stop": interface.Pause,
            "previous": interface.Previous,
        }
        function in functions and functions[function]()

    def subscribe(self, interval: float = 1.0) -> None:
        oldmetadata = self.metadatajson(tojson=False)
        print(json.dumps(oldmetadata))
        while not time.sleep(interval):
            newmetadata = self.metadatajson(tojson=False)
            if oldmetadata["xesam:title"] != newmetadata["xesam:title"]:
                oldmetadata = newmetadata
                if PCTLHandler._connected():
                    oldmetadata["mpris:artUrl"] = config["default_art"]
                print(json.dumps(oldmetadata))

    def close(self) -> None:
        self._bus.close()


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog=sys.argv[0],
        usage="%(prog)s [INTERFACE] [OPTIONS] [FLAGS]",
        description="CLI tool for managing mpd and playerctl metadata.",
    )

    parser.add_argument(
        "-I",
        "--interface",
        action="store_false",
        required=True,
        help="manage a supported player metadata",
    )

    subparser: argparse._SubParsersAction = parser.add_subparsers(
        help="mpd related metadata commands",
        required=True,
    )

    mpdparser: argparse.ArgumentParser = subparser.add_parser(name="mpd")
    mpdparser.add_argument(
        "-j",
        "--json",
        action="store_true",
        required=True,
        help="get mpd player metadata in json format",
    )

    mpdparser: argparse.ArgumentParser = subparser.add_parser(name="pctl")
    mpdparser.add_argument(
        "-j",
        "--json",
        action="store_true",
        required=True,
        help="get mpd player metadata in json format",
    )

    parsed_args: argparse.Namespace = parser.parse_args(sys.argv[1:])

# vim:filetype=python
