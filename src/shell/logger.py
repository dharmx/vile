#!/usr/bin/env --split-string=python -u

import json
import os
import pathlib
import sys

import handlers
import utils

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

INTERVAL = 0.5
DUNST_ENVS = utils.get_and_parse_env()

if __name__ == "__main__":
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
        case _:
            utils.file_add_line(
                CACHE_PATH,
                handlers.redir_to_handlers(FORMATS, DUNST_ENVS),
                HISTORY_LIMIT,
            )

# vim:filetype=python
