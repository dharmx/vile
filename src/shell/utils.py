import datetime
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

import dbus
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")

from gi.repository import GdkPixbuf, GLib, Gtk


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
    stripper = PangoStripper()
    stripper.feed(pango)
    return stripper.get_data()


def create_parents_file(file_path: str) -> None:
    pathlib.PosixPath(os.path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
    pathlib.PosixPath(file_path).touch(exist_ok=True)


def watcher(file_path: str, callback: typing.Callable, interval: int) -> None:
    try:
        old = pathlib.PosixPath(file_path).read_text()
        callback(old)
        while not time.sleep(interval):
            new = pathlib.PosixPath(file_path).read_text()
            if new != old:
                callback(new)
                old = new
    except KeyboardInterrupt:
        sys.stdout.write("Closed.\n")
    except FileNotFoundError:
        sys.stderr.write("The path does not exist!\n")
    except Exception as excep:
        sys.stderr.write(f"{excep}\n")


def get_rand_quote(file_path: str, default_quote: str) -> str:
    loaded_quotes: str = pathlib.PosixPath(file_path).read_text().strip()
    return random.choice(loaded_quotes.splitlines()) if loaded_quotes else default_quote


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

    stats["critical"] = (
        stats["critical"] * 100 / stats["total"] if stats["critical"] > 0 else 0
    )
    stats["normal"] = (
        stats["normal"] * 100 / stats["total"] if stats["normal"] > 0 else 0
    )
    stats["low"] = stats["low"] * 100 / stats["total"] if stats["low"] > 0 else 0
    return stats


def has_non_english_chars(string: str) -> dict:
    return {
        "CJK": any(unicodedata.category(char) == "Lo" for char in string),
        "CYR": any(unicodedata.category(char) == "Lu" for char in string),
    }


def get_and_parse_env() -> dict:
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

    return {
        DUNST_VARS[0]: os.getenv(DUNST_VARS[0].strip()) or "Unknown",
        DUNST_VARS[1]: (
            os.getenv(DUNST_VARS[1].strip()) or "Summary Unavailable."
        ).replace("'", "\\'"),
        DUNST_VARS[2]: (
            os.getenv(DUNST_VARS[2].strip()) or "Body Unavailable."
        ).replace("'", "\\'"),
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


def unwrap(value):
    # Try to trivially translate a dictionary's elements into nice string
    # formatting.
    if isinstance(value, dbus.ByteArray):
        return "".join([str(byte) for byte in value])
    if isinstance(value, (dbus.Array, list, tuple)):
        return [unwrap(item) for item in value]
    if isinstance(value, (dbus.Dictionary, dict)):
        return dict([(unwrap(x), unwrap(y)) for x, y in value.items()])
    if isinstance(value, (dbus.Signature, dbus.String)):
        return str(value)
    if isinstance(value, dbus.Boolean):
        return bool(value)
    if isinstance(
        value,
        (dbus.Int16, dbus.UInt16, dbus.Int32, dbus.UInt32, dbus.Int64, dbus.UInt64),
    ):
        return int(value)
    if isinstance(value, dbus.Byte):
        return bytes([int(value)])
    return value


def save_img_byte(px_args):
    # gets image data and saves it to file
    save_path = f"/tmp/image-{datetime.datetime.now().strftime('%s')}.png"
    # https://specifications.freedesktop.org/notification-spec/latest/ar01s08.html
    # https://specifications.freedesktop.org/notification-spec/latest/ar01s05.html
    GdkPixbuf.Pixbuf.new_from_bytes(
        width=px_args[0],
        height=px_args[1],
        has_alpha=px_args[3],
        data=GLib.Bytes(px_args[6]),
        colorspace=GdkPixbuf.Colorspace.RGB,
        rowstride=px_args[2],
        bits_per_sample=px_args[4],
    ).savev(save_path, "png")
    return save_path


def get_gtk_icon_path(icon_name: str, size: int, fallback_path: str) -> str:
    info = Gtk.IconTheme.get_default().lookup_icon(icon_name, size, 0)
    return info.get_filename() if info else fallback_path


def get_mime_icon_path(mimetype, size=32):
    icon = Gio.content_type_get_icon(mimetype)
    theme = Gtk.IconTheme.get_default()
    if info := theme.choose_icon(icon.get_names(), size, 0):
        print(info.get_filename())


# vim:filetype=python
