#!/usr/bin/env --split-string=python -u

import datetime
import json
import os
import pathlib
import random
import re
import sys
import time
import typing
import unicodedata
from html.parser import HTMLParser
from io import StringIO

HISTORY_LIMIT = 50
CACHE_PATH = os.path.expandvars("$XDG_CACHE_HOME/dunst/notifications.txt")
QUOTE_PATH = os.path.expandvars("$XDG_CACHE_HOME/dunst/quotes.txt")
DEFAULT_QUOTE = (
    "To fake it is to stand guard over emptiness. \u2500\u2500 Arthur Herzog"
)

FORMATS = {
    "default": "(_cardimage :identity ':::###::::XXXWWW%(DUNST_ID)s===::' :close_action './src/shell/logger.py rmid %(DUNST_ID)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '繁' :image_height 100 :image_width 100 :image '%(DUNST_ICON_PATH)s' :appname '%(DUNST_APP_NAME)s' :icon '%(DUNST_ICON_PATH)s' :icon_height 32 :icon_width 32 :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s')",
    "spotifyd": "(_cardimage :identity ':::###::::XXXWWW%(DUNST_ID)s===::' :close_action './src/shell/logger.py rmid %(DUNST_ID)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '繁' :image_height 100 :image_width 100 :image '%(DUNST_ICON_PATH)s' :appname '%(DUNST_APP_NAME)s' :icon '%(DUNST_ICON_PATH)s' :icon_height 32 :icon_width 32 :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s')",
    "ncspot": "(_cardimage :identity ':::###::::XXXWWW%(DUNST_ID)s===::' :close_action './src/shell/logger.py rmid %(DUNST_ID)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '繁' :image_height 100 :image_width 100 :image '%(DUNST_ICON_PATH)s' :appname '%(DUNST_APP_NAME)s' :icon '%(DUNST_ICON_PATH)s' :icon_height 32 :icon_width 32 :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s')",
    "Spotify": "(_cardimage :identity ':::###::::XXXWWW%(DUNST_ID)s===::' :close_action './src/shell/logger.py rmid %(DUNST_ID)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '繁' :image_height 100 :image_width 100 :image '%(DUNST_ICON_PATH)s' :appname '%(DUNST_APP_NAME)s' :icon '%(DUNST_ICON_PATH)s' :icon_height 32 :icon_width 32 :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s')",
    "shot_icon": "(_cardimage :identity ':::###::::XXXWWW%(DUNST_ID)s===::' :close_action './src/shell/logger.py rmid %(DUNST_ID)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '繁' :image_height 100 :image_width 100 :image './assets/poster.png' :appname '%(DUNST_APP_NAME)s' :icon '%(DUNST_ICON_PATH)s' :icon_height 32 :icon_width 32 :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s')",
    "notify-send": "(_cardimage :identity ':::###::::XXXWWW%(DUNST_ID)s===::' :close_action './src/shell/logger.py rmid %(DUNST_ID)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '繁' :image_height 100 :image_width 100 :image '%(DUNST_ICON_PATH)s' :appname '%(DUNST_APP_NAME)s' :icon './assets/browser.png' :icon_height 32 :icon_width 32 :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s')",
    "brightness": "(_cardprog :identity ':::###::::XXXWWW%(DUNST_ID)s===::' :close_action './src/shell/logger.py rmid %(DUNST_ID)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '繁' :image_height 100 :image_width 100 :image '%(DUNST_ICON_PATH)s' :appname '%(DUNST_APP_NAME)s' :icon '%(DUNST_ICON_PATH)s' :icon_height 32 :icon_width 32 :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s' :progress '%(DUNST_PROGRESS)s')",
    "volume": "(_cardprog :identity ':::###::::XXXWWW%(DUNST_ID)s===::' :close_action './src/shell/logger.py rmid %(DUNST_ID)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '繁' :image_height 100 :image_width 100 :image '%(DUNST_ICON_PATH)s' :appname '%(DUNST_APP_NAME)s' :icon '%(DUNST_ICON_PATH)s' :icon_height 32 :icon_width 32 :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s' :progress '%(DUNST_PROGRESS)s')",
    "shot": "(_cardscr :identity ':::###::::XXXWWW%(DUNST_ID)s===::' :close_action './src/shell/logger.py rmid %(DUNST_ID)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :delete '%(DELETE)s' :open '%(OPEN)s' :summary '%(DUNST_SUMMARY)s' :image '%(DUNST_ICON_PATH)s' :image_height 250 :image_width 100 :urgency '%(DUNST_URGENCY)s' :close '繁' :timestamp '%(DUNST_TIMESTAMP)s')",
    "todo": "(_cardradial :identity ':::###::::XXXWWW%(DUNST_ID)s===::' :close_action './src/shell/logger.py rmid %(DUNST_ID)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(DUNST_SUMMARY)s' :body '%(DUNST_BODY)s' :close '繁' :appname '%(DUNST_APP_NAME)s' :progress %(PERC)s :thickness 20.0 :total %(TOTAL)s :done %(DONE)s :timestamp '%(DUNST_TIMESTAMP)s' :urgency '%(DUNST_URGENCY)s')",
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


class PangoStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def contains_pango(string: str) -> bool:
    return any(item in string for item in ["<span>", "</span>"])


def strip_pango_tags(pango: str) -> str:
    # get your head out of the gutter
    stripper = PangoStripper()
    stripper.feed(pango)
    return stripper.get_data()


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
    except Exception:
        sys.stderr.write("Unknown Error!\n")


def file_matched_index_rm(file_path: str, pattern: str) -> None:
    posix_file_path: pathlib.PosixPath = pathlib.PosixPath(file_path)
    lines: typing.List[str] = posix_file_path.read_text().splitlines()

    rm_index_lines: typing.List[str] = [
        lines[index]
        for index in range(len(lines))
        if not re.search(pattern, lines[index])
    ]

    if len(lines) != len(rm_index_lines):
        posix_file_path.write_text("\n".join(rm_index_lines))


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


def prettify_name(name: str) -> str:
    return " ".join(
        item.capitalize()
        for item in name.replace("-", " ").replace("_", " ").split(" ")
    )


def file_add_line(file_path: str, write_contents: str, limit, top: bool = True) -> None:
    file = pathlib.PosixPath(file_path)
    file_contents = file.read_text().splitlines()
    if len(file_contents) == limit:
        file_contents = file_contents[:-1]
    file_contents = (
        [write_contents] + file_contents if top else file_contents + [write_contents]
    )
    file.write_text("\n".join(file_contents))


def parse_and_print_stats(file_contents: str) -> str:
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

    stats["critical"] = stats["critical"] * 100 / stats["total"] if stats["critical"] > 0 else 0
    stats["normal"] = stats["normal"] * 100 / stats["total"] if stats["normal"] > 0 else 0
    stats["low"] = stats["low"] * 100 / stats["total"] if stats["low"] > 0 else 0
    return stats


def has_non_english_chars(string: str) -> dict:
    return {
        "CJK": any(unicodedata.category(char) == "Lo" for char in string),
        "CYR": any(unicodedata.category(char) == "Lu" for char in string),
    }


def redir_to_handlers(appname: str) -> str:
    if contains_pango(DUNST_ENVS["DUNST_BODY"]):
        DUNST_ENVS["DUNST_BODY"] = strip_pango_tags(DUNST_ENVS["DUNST_BODY"])
    if contains_pango(DUNST_ENVS["DUNST_SUMMARY"]):
        DUNST_ENVS["DUNST_SUMMARY"] = strip_pango_tags(DUNST_ENVS["DUNST_SUMMARY"])

    DUNST_ENVS["SUMMARY_LIMITER"] = ""
    summary_lang_char_check = has_non_english_chars(DUNST_ENVS["DUNST_SUMMARY"][:15])
    if summary_lang_char_check["CJK"]:
        DUNST_ENVS["SUMMARY_LIMITER"] = 14
    elif summary_lang_char_check["CYR"]:
        DUNST_ENVS["SUMMARY_LIMITER"] = 30

    DUNST_ENVS["BODY_LIMITER"] = ""
    body_lang_char_check = has_non_english_chars(DUNST_ENVS["DUNST_BODY"][:70])
    if body_lang_char_check["CJK"]:
        DUNST_ENVS["BODY_LIMITER"] = 80
    elif body_lang_char_check["CYR"]:
        DUNST_ENVS["BODY_LIMITER"] = 110
    else:
        DUNST_ENVS["BODY_LIMITER"] = 100

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
    attributes["DUNST_APP_NAME"] = prettify_name(attributes["DUNST_APP_NAME"])
    return FORMATS["shot"] % attributes


def default_handler(attributes: dict) -> str:
    attributes["DUNST_APP_NAME"] = prettify_name(attributes["DUNST_APP_NAME"])
    return FORMATS["default"] % attributes


def notify_send_handler(attributes: dict) -> str:
    attributes["DUNST_APP_NAME"] = prettify_name(attributes["DUNST_APP_NAME"])
    return FORMATS["notify-send"] % attributes


def brightness_handler(attributes: dict) -> str:
    attributes["DUNST_APP_NAME"] = prettify_name(attributes["DUNST_APP_NAME"])
    return FORMATS["brightness"] % attributes


def volume_handler(attributes: dict) -> str:
    attributes["DUNST_APP_NAME"] = prettify_name(attributes["DUNST_APP_NAME"])
    return FORMATS["volume"] % attributes


def todo_handler(attributes: dict) -> str:
    splitted = attributes["DUNST_BODY"].split(" ")
    attributes["TOTAL"] = int(splitted[4])
    attributes["DONE"] = int(splitted[0])
    attributes["PERC"] = (attributes["DONE"] / attributes["TOTAL"]) * 100
    attributes["DUNST_APP_NAME"] = prettify_name(attributes["DUNST_APP_NAME"])
    return FORMATS["todo"] % attributes


def shot_icon_handler(attributes: dict) -> str:
    attributes["DUNST_APP_NAME"] = prettify_name(attributes["DUNST_APP_NAME"])
    return FORMATS["shot_icon"] % attributes


def get_rand_quote(file_path: str, default_quote: str) -> str:
    loaded_quotes: str = pathlib.PosixPath(file_path).read_text().strip()
    return random.choice(loaded_quotes.splitlines()) if loaded_quotes else default_quote


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        args = ["dummy", "dummy"]
    match args[1]:
        case "subscribe":
            watcher(
                CACHE_PATH,
                lambda contents: sys.stdout.write(
                    "(box :spacing 20 :orientation 'vertical' :space-evenly false " +
                    # handle empty
                    contents.replace("\n", " ") + ")\n"
                    if contents.strip()
                    else (
                        (FORMATS["empty"] + "\n")
                        % {"QUOTE": get_rand_quote(QUOTE_PATH, DEFAULT_QUOTE)}
                    )
                ),
            )
        case "rmid":
            file_matched_index_rm(
                CACHE_PATH, f":identity ':::###::::XXXWWW{sys.argv[2]}===::'"
            )
        case "stats":
            sys.stdout.write(
                json.dumps(
                    parse_and_print_stats(pathlib.PosixPath(CACHE_PATH).read_text())
                )
                + "\n"
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
            file_add_line(
                CACHE_PATH,
                redir_to_handlers(DUNST_ENVS["DUNST_APP_NAME"]),
                HISTORY_LIMIT,
            )

# vim:filetype=python
