#!/usr/bin/env --split-string=python -u

import json
import os
import pathlib
import sys

import handlers
import utils
import cache

FORMATS = {
    "spotifyd": "(_cardimage :identity ':::###::::XXXWWW%(id)s===::' :close_action './src/shell/logger.py rmid %(id)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(summary)s' :body '%(body)s' :close '繁' :image_height 100 :image_width 100 :image '%(iconpath)s' :appname '%(appname)s' :icon '%(iconpath)s' :icon_height 32 :icon_width 32 :timestamp '%(TIMESTAMP)s' :urgency '%(URGENCY)s')",
    "ncspot": "(_cardimage :identity ':::###::::XXXWWW%(id)s===::' :close_action './src/shell/logger.py rmid %(id)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(summary)s' :body '%(body)s' :close '繁' :image_height 100 :image_width 100 :image '%(iconpath)s' :appname '%(appname)s' :icon '%(iconpath)s' :icon_height 32 :icon_width 32 :timestamp '%(TIMESTAMP)s' :urgency '%(URGENCY)s')",
    "Spotify": "(_cardimage :identity ':::###::::XXXWWW%(id)s===::' :close_action './src/shell/logger.py rmid %(id)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(summary)s' :body '%(body)s' :close '繁' :image_height 100 :image_width 100 :image '%(iconpath)s' :appname '%(appname)s' :icon '%(iconpath)s' :icon_height 32 :icon_width 32 :timestamp '%(TIMESTAMP)s' :urgency '%(URGENCY)s')",

    "shot_icon": "(_cardimage :identity ':::###::::XXXWWW%(id)s===::' :close_action './src/shell/logger.py rmid %(id)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(summary)s' :body '%(body)s' :close '繁' :image_height 100 :image_width 100 :image './assets/poster.png' :appname '%(appname)s' :icon '%(iconpath)s' :icon_height 32 :icon_width 32 :timestamp '%(TIMESTAMP)s' :urgency '%(URGENCY)s')",
    "shot": "(_cardscr :identity ':::###::::XXXWWW%(id)s===::' :close_action './src/shell/logger.py rmid %(id)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :delete '%(DELETE)s' :open '%(OPEN)s' :summary '%(summary)s' :image '%(iconpath)s' :image_height 250 :image_width 100 :urgency '%(URGENCY)s' :close '繁' :timestamp '%(TIMESTAMP)s')",

    "default": "(_cardimage :identity ':::###::::XXXWWW%(id)s===::' :close_action './src/shell/logger.py rmid %(id)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(summary)s' :body '%(body)s' :close '繁' :image_height 100 :image_width 100 :image '%(iconpath)s' :appname '%(appname)s' :icon '%(iconpath)s' :icon_height 32 :icon_width 32 :timestamp '%(TIMESTAMP)s' :urgency '%(URGENCY)s')",
    "notify-send": "(_cardimage :identity ':::###::::XXXWWW%(id)s===::' :close_action './src/shell/logger.py rmid %(id)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(summary)s' :body '%(body)s' :close '繁' :image_height 100 :image_width 100 :image '%(iconpath)s' :appname '%(appname)s' :icon './assets/browser.png' :icon_height 32 :icon_width 32 :timestamp '%(TIMESTAMP)s' :urgency '%(URGENCY)s')",
    "empty": "(box :class 'disclose-empty-box' :height 750 :orientation 'vertical' :space-evenly false (image :class 'disclose-empty-banner' :valign 'end' :vexpand true :path './assets/wedding-bells.png' :image-width 250 :image-height 250) (label :vexpand true :valign 'start' :wrap true :class 'disclose-empty-label' :text '%(QUOTE)s'))",

    "brightness": "(_cardprog :identity ':::###::::XXXWWW%(id)s===::' :close_action './src/shell/logger.py rmid %(id)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(summary)s' :body '%(body)s' :close '繁' :image_height 100 :image_width 100 :image '%(iconpath)s' :appname '%(appname)s' :icon '%(iconpath)s' :icon_height 32 :icon_width 32 :timestamp '%(TIMESTAMP)s' :urgency '%(URGENCY)s' :progress '%(progress)s')",
    "todo": "(_cardradial :identity ':::###::::XXXWWW%(id)s===::' :close_action './src/shell/logger.py rmid %(id)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(summary)s' :body '%(body)s' :close '繁' :appname '%(appname)s' :progress %(PERC)s :thickness 20.0 :total %(TOTAL)s :done %(DONE)s :timestamp '%(TIMESTAMP)s' :urgency '%(URGENCY)s')",
    "volume": "(_cardprog :identity ':::###::::XXXWWW%(id)s===::' :close_action './src/shell/logger.py rmid %(id)s' :limit_body '%(BODY_LIMITER)s' :limit_summary '%(SUMMARY_LIMITER)s' :summary '%(summary)s' :body '%(body)s' :close '繁' :image_height 100 :image_width 100 :image '%(iconpath)s' :appname '%(appname)s' :icon '%(iconpath)s' :icon_height 32 :icon_width 32 :timestamp '%(TIMESTAMP)s' :urgency '%(URGENCY)s' :progress '%(progress)s')",
}


if __name__ == "__main__":
    config = json.loads(
        pathlib.PosixPath(
            os.path.expandvars("$XDG_CONFIG_HOME/eww/.config.json")
        ).read_text()
    )["notify"]

    HISTORY_LIMIT = config["limit"]
    CACHE_PATH = os.path.expandvars(config["cache_path"])
    QUOTE_PATH = os.path.expandvars(config["quote_path"])
    DEFAULT_QUOTE = config["default_quote"]
    INTERVAL = config["interval"]

    args = sys.argv
    if len(args) < 2:
        args = ["dummy", "dummy"]
    match args[1]:
        case "subscribe":
            utils.create_parents_file(CACHE_PATH)
            utils.watcher(
                CACHE_PATH,
                lambda contents: sys.stdout.write(
                    "(box :spacing 20 :orientation 'vertical' :space-evenly false " +
                    # handle empty
                    contents.replace("\n", " ") + ")\n"
                    if contents.strip()
                    else (
                        (FORMATS["empty"] + "\n")
                        % {"QUOTE": utils.get_rand_quote(QUOTE_PATH, DEFAULT_QUOTE)}
                    )
                ),
                INTERVAL,
            )
        case "rmid":
            utils.file_matched_index_rm(
                CACHE_PATH, f":identity ':::###::::XXXWWW{sys.argv[2]}===::'"
            )
        case "stats":
            sys.stdout.write(
                json.dumps(
                    utils.parse_and_print_stats(
                        pathlib.PosixPath(CACHE_PATH).read_text()
                    )
                )
                + "\n"
            )
        case "rm":
            utils.file_rm_line(CACHE_PATH, int(sys.argv[2]))
        case "quote":
            sys.stdout.write(utils.get_rand_quote(QUOTE_PATH, DEFAULT_QUOTE))
        case "cls":
            pathlib.PosixPath(CACHE_PATH).write_text("")
        case "init":
            def master_callback(details: dict):
                details["TIMESTAMP_FORMAT"] = config["timestamp"]
                saved_path = handlers.redir_to_handlers(FORMATS, details)
                utils.file_add_line(
                    CACHE_PATH,
                    saved_path,
                    HISTORY_LIMIT,
                )

            cache.Eavesdropper(master_callback).eavesdrop()

# vim:filetype=python
