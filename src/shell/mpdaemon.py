#!/usr/bin/env --split-string=python -u
"""Script to cache and fetch the current track details for MPD"""

# Authored By dharmx <dharmx.dev@gmail.com> under:
# GNU GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007
#
# Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
# Everyone is permitted to copy and distribute verbatim copies
# of this license document, but changing it is not allowed.
#
# Permissions of this strong copyleft license are conditioned on
# making available complete source code of licensed works and
# modifications, which include larger works using a licensed work,
# under the same license. Copyright and license notices must be
# preserved. Contributors provide an express grant of patent rights.
#
# Read the complete license here:
# <https://github.com/dharmx/vile/blob/main/LICENSE.txt>

import json
import os
import pathlib
import utils
import time

import mpd
from mpd.base import CommandError

class MPDHandler:
    """A class that represents the MPD daemon."""
    def __init__(self, prefix: str, cache, default):
        """Initialize the mpd client and get all the boiler plate code out of the way.
        Then check if the cache paths and directory exists or, not. Create them if they don't.

        Arguments:
            prefix: The directory of the source i.e. the place where your music is stored.
                    This must be the same as your mpd config.
            cache: The directory where all of the cover art caches are stored.
            default: The path to the default / fallback cover art.
        """
        self._client: mpd.MPDClient = mpd.MPDClient()
        self._client.timeout = 3
        self._client.connect("localhost", 6600)

        # equivalent: mkdir --parents
        self.prefix, self.cache, self.default = prefix, cache, default
        pathlib.Path(self.prefix).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.cache).mkdir(parents=True, exist_ok=True)

    def _validatepath(self, path: str) -> str:
        """Add an extra slash if the file is in a sub-directory as passing 
        a.ext to dirname will result in returning an empty string.

        Arguments:
            path: The location of the file.
        """
        path = os.path.dirname(path)
        return f"{path}/" if "/" in path or path else path

    def _embeddedcover(self, key: str) -> str | bytes:
        """If there is no embedded cover art in the current playing track file then
        return a path to the fallback image instead.

        Arguments:
            key: the name of the track.

        Returns:
            A str when there is no embedded cover art, bytes otherwise.
        """
        content = {"binary": self.default}
        try:
            self._client.readpicture(key)
            content = self._client.albumart(key)
        except CommandError:
            content = {"binary": self.default}
        return content["binary"]

    def get(self, key: str) -> str:
        """Return the path to the cover art if it exists.

        Arguments:
            key: Title of the song.
        """
        music: str = (
            f"{self.cache}/{self._validatepath(key)}{pathlib.Path(key).stem}.png"
        )
        return music if os.path.exists(music) else self.default

    def create(self, key: str) -> bool:
        """If embedded cover exists for the current track then it fetches
        that in the form of bytes and then writes that to a file. In other
        words it caches that cover art.

        Arguments:
            key: Path to the current playing song.

        Returns:
            A bool, True if a cache file is created, False otherwise.
        """
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

    def metadatajson(self, tojson=True) -> str | dict:
        """Fetch current song metadata, tags and player statistics
        and pack the cover image as well.

        Arguments:
            tojson: Return json format string if set to True, otherwise just print a raw pythonic dict.

        Returns:
            A JSON str if tojson is True, a dict otherwise.
        """
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
        metadata["current"]["x"] = self._client.status()

        if "xfade" not in metadata["current"]["x"]:
            metadata["current"]["x"]["xfade"] = 0

        # simplify image + apply dither for handling gradients + get histogram -> it will yield 8 hex codes
        colors = utils.img_dark_bright_col(metadata['current']['file'])

        # pick out the brightest and the darkest color and use that as foreground | background.
        metadata["current"]["bright"] = colors[3]
        metadata["current"]["dark"] = colors[-1]
        return json.dumps(metadata) if tojson else metadata


    def cacheplaylist(self):
        """Cache all of the cover art in the current playlist."""
        [self.create(file[6:]) for file in self._client.playlist()]

    def cachedatatbase(self):
        """Cache all tracks that are currently in the database."""
        self._client.rescan()
        self._client.update()

        for file in self._client.listall():
            todict: dict = dict(file)
            if "directory" not in todict:
                self.create(todict["file"])

    def subscribe(self, interval: float = 1.0) -> str:
        """A simple watcher that monitors track changes. And prints
        the current track info on track change in JSON format.

        Arguments:
            interval: Interval between checking the current playing track for changes.
        """
        old = self.metadatajson(tojson=False)["current"]
        print(json.dumps(old))
        while not time.sleep(interval):
            new = self.metadatajson(tojson=False)["current"]
            old_formatted = f"{old['artist']}-{old['title']}-{old['album']}-{old['status']}-{old['x']['repeat']}-{old['x']['volume']}-{old['x']['random']}-{old['x']['single']}-{old['x']['consume']}-{old['x']['xfade']}"
            new_formatted = f"{new['artist']}-{new['title']}-{new['album']}-{new['status']}-{new['x']['repeat']}-{new['x']['volume']}-{new['x']['random']}-{new['x']['single']}-{new['x']['consume']}-{new['x']['xfade']}"

            if old_formatted != new_formatted:
                print(json.dumps(new))
                old = new

    def close(self):
        """Close the close and then disconnect from the mpd client."""
        self._client.close()
        self._client.disconnect()


if __name__ == "__main__":
    with open(os.path.expandvars("$XDG_CONFIG_HOME/eww/ewwrc"), encoding="utf8") as file:
        # load config values
        config: dict = json.loads(file.read())["player"]
        config["default_art"] = os.path.expandvars(config["default_art"])
        config["mpd_cache"] = os.path.expandvars(config["mpd_cache"])

    handler = MPDHandler(
        os.path.expandvars("$XDG_MUSIC_DIR"),
        config["mpd_cache"],
        config["default_art"],
    )

    # cache the database and look if there are any music files that haven't been cached yet
    # if there are then cache them.
    handler.cachedatatbase()
    handler.subscribe(1)
    handler.close()

# vim:filetype=python
