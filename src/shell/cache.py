import datetime
import os
import pathlib
import sys
import typing

import dbus
import utils
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib


class Urgency:
    LOW = b"\x00"
    NORMAL = b"\x01"
    CRITICAL = b"\x02"


class Eavesdropper:
    def __init__(
        self,
        callback: typing.Callable = print,
        cache_dir: str = "/tmp"
    ):
        self.callback = callback
        self.cache_dir = f"{os.path.expandvars(cache_dir)}/image-data"
        pathlib.PosixPath(self.cache_dir).mkdir(parents=True, exist_ok=True)

    def _message_callback(self, _, message):
        if type(message) != dbus.lowlevel.MethodCallMessage:
            return

        args_list = message.get_args_list()
        args_list = [utils.unwrap(item) for item in args_list]

        details = {
            "appname": args_list[0].strip() or "Unknown",
            "summary": args_list[3].strip() or "Summary Unavailable.",
            "body": args_list[4].strip() or "Body Unavailable.",
            "id": datetime.datetime.now().strftime("%s"),
            "urgency": "unknown",
        }

        if "urgency" in args_list[6]:
            details["urgency"] = args_list[6]["urgency"]

        if args_list[2].strip():
            if "/" in args_list[2] or "." in args_list[2]:
                details["iconpath"] = args_list[2]
            else:
                details["iconpath"] = utils.get_gtk_icon_path(args_list[2])
        else:
            details["iconpath"] = utils.get_gtk_icon_path("custom-notification")

        if "image-data" in args_list[6]:
            details["iconpath"] = f"{self.cache_dir}/{details['appname']}-{details['id']}.png"
            utils.save_img_byte(args_list[6]["image-data"], details["iconpath"])

        if "value" in args_list[6]:
            print(args_list[6]["value"])
            details["progress"] = args_list[6]["value"]

        self.callback(details)

    def eavesdrop(
        self,
        timeout: int or bool = False,
        timeout_callback: typing.Callable = print
    ):
        DBusGMainLoop(set_as_default=True)

        rules = {
            "interface": "org.freedesktop.Notifications",
            "member": "Notify",
            "eavesdrop": "true",  # https://bugs.freedesktop.org/show_bug.cgi?id=39450
        }

        bus = dbus.SessionBus()
        bus.add_match_string(
            ",".join([f"{key}={value}" for key, value in rules.items()])
        )
        bus.add_message_filter(self._message_callback)

        try:
            loop = GLib.MainLoop()
            if timeout:
                GLib.set_timeout(timeout, timeout_callback)
            loop.run()
        except (KeyboardInterrupt, Exception) as excep:
            sys.stderr.write(str(excep) + "\n")
            bus.close()


# vim:filetype=python
