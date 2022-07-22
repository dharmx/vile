#!/usr/bin/env python

import contextlib
import typing

import dbus
import utils
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib


class Eavesdropper:
    def __init__(
        self,
        callback: typing.Callable
        or None = (lambda *args, **kwargs: print(f"{args}::::{kwargs}")),
        timeout: bool or int = False,
        timeout_callback: typing.Callable
        or None = (lambda *args, **kwargs: print(f"{args}::::{kwargs}")),
    ):
        self.timeout = timeout
        self.callback = callback
        self.timeout_callback = timeout_callback

    def _message_callback(self, _, message):
        if type(message) != dbus.lowlevel.MethodCallMessage:
            return
        args_list = message.get_args_list()
        args_list = [utils.unwrap(item) for item in args_list]
        details = {
            "appname": args_list[0],
            "summary": args_list[3],
            "body": args_list[4],
            "urgency": args_list[6]["urgency"],
            "iconpath": None,
        }
        if args_list[2]:
            details["iconpath"] = args_list[2]
        with contextlib.suppress(KeyError):
            details["iconpath"] = utils.save_img_byte(args_list[6]["image-data"])

        if self.callback:
            self.callback(details)

    def eavesdrop(self):
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
            if self.timeout:
                GLib.set_timeout(self.timeout, self.timeout_callback)
            loop.run()
        except KeyboardInterrupt:
            bus.close()


Eavesdropper().eavesdrop()

# vim:filetype=python
