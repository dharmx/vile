#!/usr/bin/env --split-string=python -u

# TODO: Implement caching
# TODO: Implement image and text based caching
# TODO: Replicate the quote script

import json
import os
import pathlib
import sys
import time
import typing

dunst_vars = [
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
DUNST_ENV = {
    dunst_vars[0]: os.getenv(dunst_vars[0], "Unknown"),
    dunst_vars[1]: os.getenv(dunst_vars[1], "Summary Unavailable."),
    dunst_vars[2]: os.getenv(dunst_vars[2], "Body Unavailable."),
    dunst_vars[3]: os.getenv(dunst_vars[3], ""),
    dunst_vars[4]: os.getenv(dunst_vars[4], "Unknown"),
    dunst_vars[5]: os.getenv(dunst_vars[5], "Unknown"),
    dunst_vars[6]: os.getenv(dunst_vars[6], "Unknown"),
    dunst_vars[7]: os.getenv(dunst_vars[7], "Unknown"),
    dunst_vars[8]: os.getenv(dunst_vars[8], "Unknown"),
    dunst_vars[9]: os.getenv(dunst_vars[9], "Unknown"),
    dunst_vars[10]: os.getenv(dunst_vars[10], "Unknown"),
    dunst_vars[11]: os.getenv(dunst_vars[11], "Unknown"),
    dunst_vars[12]: os.getenv(dunst_vars[12], "Unknown"),
    dunst_vars[13]: os.getenv(dunst_vars[13], "Unknown"),
}


def watcher(file_path: str, callback: typing.Callable) -> None:
    INTERVAL = config["logger"]["interval"]
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


def file_in_line(file_path: str, write_contents: str, position: bool = True) -> None:
    file = pathlib.PosixPath(file_path)
    file_contents = file.read_text().splitlines()
    write_contents += "\n"
    file_contents = (
        [write_contents] + file_contents
        if position
        else file_contents + [write_contents]
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


if __name__ == "__main__":
    with open("./.config.json") as file:
        config: dict = json.load(file)

# vim:filetype=python
