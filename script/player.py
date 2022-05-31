import argparse
import json
import os
import sys
from pathlib import Path

import mpd
from mutagen import mp3

with open("../.config.json", encoding="utf8") as file:
    config: dict = json.loads(file.read())["player"]


class MpdCacheHandler:
    def __init__(self, prefix, cache, default) -> None:
        # equivalent: mkdir --parents
        Path(prefix).mkdir(parents=True, exist_ok=True)
        Path(cache).mkdir(parents=True, exist_ok=True)
        self.prefix, self.cache, self.default = (
            os.path.expandvars(path) for path in (prefix, cache, default)
        )

    def _validatepath(path: str) -> str:
        path = os.path.dirname(path)
        return path + "/" if "/" in path or path else path

    def _embeddedcover(self, key: str) -> None or bytes:
        meta = mp3.EasyMP3(f"{self.prefix}/{key}").tags._EasyID3__id3._DictProxy__dict
        # if metadata contains APIC:* key then the file is an mp3 and has cover art
        checked = [meta[item] for item in meta.keys() if item.startswith("APIC")]
        # return byte content
        return None if not len(checked) else checked.pop().data

    def get(self, key: str) -> str:
        music = f"{self.cache}/{os.path.dirname(key)}/{Path(key).stem}.png"
        return music if os.path.exists(music) else self.default

    def create(self, key: str) -> bool:
        # a/b/c/d.e: dirname -> a/b/c | stem -> d
        # generate cache path -> cache + dirname + stem + ".png"
        Path(os.path.dirname(f"{self.cache}/{key}")).mkdir(parents=True, exist_ok=True)
        cachefull = f"{MpdCacheHandler._validatepath(key)}{Path(key).stem}"

        if not os.path.exists(f"{self.cache}/{cachefull}.png"):
            # try fetch the embedded cover in the mp3 file
            covercontent = self._embeddedcover(f"{cachefull}.mp3")

            if covercontent:  # check if mp3 has cover art
                with open(f"{self.cache}/{cachefull}.png", "wb") as target:
                    target.write(covercontent)  # then write bytes to file
                return True
            return False
        return False  # will return True iff a file is created


# TODO: finish this within today
class MPDHandler:
    def __init__(self) -> None:
        """Setup MPD client for use."""
        self._client: mpd.MPDClient = mpd.MPDClient()
        self._client.timeout = 3
        self._client.connect("localhost", 6600)

    def toggle(self, function) -> bool:
        currentstatus = json.loads(self.get_metadata_json())
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
            if self.get_metadata_json(True)["state"] == "play"
            else self._client.play(),
        }
        function in functions and functions[function]()

    def get_metadata_json(self, tojson=True) -> str:
        metadata: dict = self._client.status()
        metadata["current"] = self._client.currentsong()
        metadata["stats"] = self._client.stats()
        return metadata if not tojson else json.dumps(metadata)

    def close(self) -> None:
        self._client.close()
        self._client.disconnect()


class PCTLCacheHandler:
    pass


class PCTLHandler:
    pass


parser: argparse.ArgumentParser = argparse.ArgumentParser(
    prog="playman",
    usage="%(prog)s [INTERFACE] [OPTIONS] [FLAGS]",
    description="CLI tool for managing mpd and playerctl metadata.",
)

parser.add_argument(
    "-I",
    "--interface",
    action="store_false",
    help="manage a supported player metadata",
)

subparser: argparse._SubParsersAction = parser.add_subparsers(
    help="mpd related metadata commands"
)

mpdparser: argparse.ArgumentParser = subparser.add_parser(name="mpd")
mpdparser.add_argument(
    "-j",
    "--json",
    action="store_true",
    help="get mpd player metadata in json format",
)

parsed_args: argparse.Namespace = parser.parse_args(sys.argv[1:])
handler = MPDHandler()
print(handler.get_metadata_json(tojson=True))
handler.close()

# vim:filetype=python
