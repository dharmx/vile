#!/usr/bin/env --split-string=python -u

# TODO: Implement caching
# TODO: Implement image and text based caching
# TODO: Replicate the quote script

import datetime
import json
import os
import pathlib
import random
import sys
import time
import typing

CACHE_PATH = os.path.expandvars("$XDG_CACHE_HOME/dunst/notifications.txt")
QUOTE_PATH = os.path.expandvars("$XDG_CACHE_HOME/dunst/quotes.txt")
DEFAULT_QUOTE = "To fake it is to stand guard over emptiness. \u2500\u2500 Arthur Herzog"

FORMATS = {
    "default": "(_cardimage :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '' :image_height 100 :image_width 100 :image '%(DUNST_ICON_PATH)s' :appname '%(DUNST_APP_NAME)s' :icon '%(DUNST_ICON_PATH)s' :icon_height 32 :icon_width 32 :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s')",
    "spotifyd": "(_cardimage :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '' :image_height 100 :image_width 100 :image '%(DUNST_ICON_PATH)s' :appname '%(DUNST_APP_NAME)s' :icon '%(DUNST_ICON_PATH)s' :icon_height 32 :icon_width 32 :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s')",
    "ncspot": "(_cardimage :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '' :image_height 100 :image_width 100 :image '%(DUNST_ICON_PATH)s' :appname '%(DUNST_APP_NAME)s' :icon '%(DUNST_ICON_PATH)s' :icon_height 32 :icon_width 32 :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s')",
    "Spotify": "(_cardimage :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '' :image_height 100 :image_width 100 :image '%(DUNST_ICON_PATH)s' :appname '%(DUNST_APP_NAME)s' :icon '%(DUNST_ICON_PATH)s' :icon_height 32 :icon_width 32 :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s')",
    "shot_icon": "(_cardimage :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '' :image_height 100 :image_width 100 :image './assets/poster.png' :appname '%(DUNST_APP_NAME)s' :icon '%(DUNST_ICON_PATH)s' :icon_height 32 :icon_width 32 :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s')",
    "notify-send": "(_cardimage :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '' :image_height 100 :image_width 100 :image '%(DUNST_ICON_PATH)s' :appname '%(DUNST_APP_NAME)s' :icon './assets/browser.png' :icon_height 32 :icon_width 32 :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s')",
    "brightness": "(_cardprog :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '' :image_height 100 :image_width 100 :image '%(DUNST_ICON_PATH)s' :appname '%(DUNST_APP_NAME)s' :icon '%(DUNST_ICON_PATH)s' :icon_height 32 :icon_width 32 :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s' :progress '%(DUNST_PROGRESS)s')",
    "volume": "(_cardprog :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '' :image_height 100 :image_width 100 :image '%(DUNST_ICON_PATH)s' :appname '%(DUNST_APP_NAME)s' :icon '%(DUNST_ICON_PATH)s' :icon_height 32 :icon_width 32 :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s' :progress '%(DUNST_PROGRESS)s')",
    "shot": "(_cardscr :delete '%(DELETE)s' :open '%(OPEN)s' :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :image '%(DUNST_ICON_PATH)s' :image_height 250 :image_width 100 :urgency '%(DUNST_URGENCY)s' :close '' :timestamp '%(DUNST_TIMESTAMP)s')",
    "todo": "(_cardradial :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '' :appname '%(DUNST_APP_NAME)s' :progress %(PERC)s :thickness 20.0 :total %(TOTAL)s :done %(DONE)s :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s')",
    "empty": "(box :class 'disclose-empty-box' :height 750 :orientation 'vertical' :space-evenly false (image :class 'disclose-empty-banner' :valign 'end' :vexpand true :path './assets/wedding-bells.png' :image-width 250 :image-height 250) (label :vexpand true :valign 'start' :wrap true :class 'disclose-empty-label' :text '%(QUOTE)s'))",
}

DUNST_VARS = [
    "DUNST_APP_NAME",
    "DUNST_SUMMARY",
    "DUNST_BODY",
    "DUNST_ICON_PATH",
    "DUNST_URGENCY",
    "DUNST_ID",
    "DUNST_PROGRESS",
    "DUNST_CATEGORY",
    "DUNST_STACK_TAG",
    "DUNST_URLS",
    "DUNST_TIMEOUT",
    "DUNST_TIMESTAMP",
    "DUNST_DESKTOP_ENTRY",
    "DUNST_STACK_TAG",
]

INTERVAL = 0.5
DUNST_ENVS = {
    DUNST_VARS[0]: os.getenv(DUNST_VARS[0].strip()) or "Unknown",
    DUNST_VARS[1]: (os.getenv(DUNST_VARS[1].strip()) or "Summary Unavailable.").replace(
        "'", "\\'"
    ),
    DUNST_VARS[2]: (os.getenv(DUNST_VARS[2].strip()) or "Body Unavailable.").replace(
        "'", "\\'"
    ),
    DUNST_VARS[3]: os.getenv(DUNST_VARS[3].strip()) or "./assets/browser.png",
    DUNST_VARS[4]: os.getenv(DUNST_VARS[4].strip()) or "Normal",
    DUNST_VARS[5]: os.getenv(DUNST_VARS[5].strip()) or "N/A",
    DUNST_VARS[6]: os.getenv(DUNST_VARS[6].strip()) or "N/A",
    DUNST_VARS[7]: os.getenv(DUNST_VARS[7].strip()) or "N/A",
    DUNST_VARS[8]: os.getenv(DUNST_VARS[8].strip()) or "N/A",
    DUNST_VARS[9]: os.getenv(DUNST_VARS[9].strip()) or "N/A",
    DUNST_VARS[10]: os.getenv(DUNST_VARS[10].strip()) or 5,
    DUNST_VARS[11]: datetime.datetime.now().strftime("%H:%M"),
    DUNST_VARS[12]: os.getenv(DUNST_VARS[12].strip()) or "notify-send",
    DUNST_VARS[13]: os.getenv(DUNST_VARS[13].strip()) or "notify-send",
}


def watcher(file_path: str, callback: typing.Callable) -> None:
    try:
        old = pathlib.PosixPath(file_path).read_text()
        callback(old)
        while not time.sleep(INTERVAL):
            new = pathlib.PosixPath(file_path).read_text()
            if new != old:
                callback(new)
                old = new
    except KeyboardInterrupt:
        sys.stdout.write("Closed.\n")
    except FileNotFoundError:
        sys.stderr.write("The path does not exist!\n")


def file_rm_line(file_path: str, position: int or bool or range = True) -> bool:
    file = pathlib.PosixPath(file_path)
    match str(type(position)):
        case "<class 'int'>":
            file_contents = file.read_text().splitlines()
            if position == 0:
                file_rm_line(file_path, position=True)
                return
            elif position == len(file_contents) - 1:
                file_rm_line(file_path, position=False)
                return
            line_removed_contents = []
            for index in range(len(file_contents)):
                if index != position:
                    line_removed_contents += [file_contents[index]]
            file.write_text("\n".join(line_removed_contents))
        case "<class 'bool'>":
            file_contents = file.read_text().splitlines()
            file_contents = file_contents[1:] if position else file_contents[:-1]
            file.write_text("\n".join(file_contents))
        case "<class 'range'>":
            if not position:
                file.write_text("")
                return
            file_contents = file.read_text().splitlines()
            write_contents = []
            for index in range(len(file_contents)):
                if index not in position:
                    write_contents += [file_contents[index]]
            file.write_text("\n".join(write_contents))


def file_add_line(file_path: str, write_contents: str, top: bool = True) -> None:
    file = pathlib.PosixPath(file_path)
    file_contents = file.read_text().splitlines()
    file_contents = (
        [write_contents] + file_contents if top else file_contents + [write_contents]
    )
    file.write_text("\n".join(file_contents))


def parse_stats(file_contents: str) -> None:
    stats = {"critical": 0, "low": 0, "normal": 0, "total": 0}
    for line in file_contents.splitlines():
        if "CRITICAL" in line:
            stats["critical"] += 1
            stats["total"] += 1
        elif "LOW" in line:
            stats["low"] += 1
            stats["total"] += 1
        elif "NORMAL" in line:
            stats["normal"] += 1
            stats["total"] += 1
    sys.stdout.write(json.dumps(stats) + "\n")


def redir_to_handlers(appname: str) -> str:
    match appname:
        case "notify-send":
            return notify_send_handler(DUNST_ENVS)
        case "volume":
            return volume_handler(DUNST_ENVS)
        case "brightness":
            return brightness_handler(DUNST_ENVS)
        case "shot":
            return shot_handler(DUNST_ENVS)
        case "todo":
            return todo_handler(DUNST_ENVS)
        case _:
            return default_handler(DUNST_ENVS)


def shot_handler(attributes: dict) -> str:
    # TODO: Make this better
    attributes["DELETE"] = f"rm --force \\'{attributes['DUNST_ICON_PATH']}\\'"
    attributes["OPEN"] = f"xdg-open \\'{attributes['DUNST_ICON_PATH']}\\'"
    return FORMATS["shot"] % attributes


def default_handler(attributes: dict) -> str:
    return FORMATS["default"] % attributes


def notify_send_handler(attributes: dict) -> str:
    return FORMATS["notify-send"] % attributes


def brightness_handler(attributes: dict) -> str:
    return FORMATS["brightness"] % attributes


def volume_handler(attributes: dict) -> str:
    return FORMATS["volume"] % attributes


def todo_handler(attributes: dict) -> str:
    splitted = attributes["DUNST_BODY"].split(" ")
    attributes["TOTAL"] = int(splitted[4])
    attributes["DONE"] = int(splitted[0])
    attributes["PERC"] = (attributes["DONE"] / attributes["TOTAL"]) * 100
    return FORMATS["todo"] % attributes


def shot_icon_handler(attributes: dict) -> str:
    return FORMATS["shot_icon"] % attributes


def get_rand_quote(file_path: str, default_quote: str) -> str:
    loaded_quotes: str = pathlib.PosixPath(file_path).read_text().strip()
    return random.choice(loaded_quotes.splitlines()) if loaded_quotes else default_quote


if __name__ == "__main__":
    match sys.argv[1]:
        case "subscribe":
            watcher(
                CACHE_PATH,
                lambda contents: sys.stdout.write(
                    "(box :spacing 20 :orientation 'vertical' :space-evenly false " +
                    # handle empty
                    contents.replace("\n", " ") + ")\n"
                    if contents.strip()
                    else ((FORMATS["empty"] + "\n") % {"QUOTE": get_rand_quote(QUOTE_PATH, DEFAULT_QUOTE)})
                ),
            )
        case "rm":
            file_rm_line(CACHE_PATH, int(sys.argv[2]))
        case "quote":
            sys.stdout.write(get_rand_quote(QUOTE_PATH, DEFAULT_QUOTE))
        case "cls":
            os.system(
                "killall dunst && dunst -conf ~/.config/dunst/config.ini & disown"
            )
            pathlib.PosixPath(CACHE_PATH).write_text("")
        case _:
            file_add_line(CACHE_PATH, redir_to_handlers(DUNST_ENVS["DUNST_APP_NAME"]))

# vim:filetype=python
