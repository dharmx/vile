#!/usr/bin/env --split-string=python -u

import json
import os
import pathlib
import subprocess
import time

import mpd
from mpd.base import CommandError


class MPDHandler:
    def __init__(self, prefix, cache, default) -> None:
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
        metadata["current"]["status"] = self._client.status()["state"]

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
            old_formatted = f"{old['artist']}-{old['title']}-{old['album']}-{old['status']}"
            new_formatted = f"{new['artist']}-{new['title']}-{new['album']}-{new['status']}"
            if old_formatted != new_formatted:
                print(json.dumps(new))
                old = new

    def close(self) -> None:
        self._client.close()
        self._client.disconnect()


if __name__ == "__main__":
    with open("./.config.json", encoding="utf8") as file:
        config: dict = json.loads(file.read())["player"]
        config["default_art"] = os.path.expandvars(config["default_art"])
        config["mpd_cache"] = os.path.expandvars(config["mpd_cache"])

    handler = MPDHandler(
        os.path.expandvars("$XDG_MUSIC_DIR"),
        config["mpd_cache"],
        config["default_art"],
    )
    handler.cachedatatbase()
    handler.subscribe(1)
    handler.close()

# vim:filetype=python
