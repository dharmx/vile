#!/usr/bin/env python

import json
import os
import pathlib
import subprocess
import praw


def get_reddit_password(config: dict) -> str:
    # sourcery skip: inline-immediately-returned-variable
    password = None
    password_method = config["reddit"]["password_method"].split(":")
    match password_method[0]:
        case "command":
            password_path = pathlib.PosixPath(
                f"{config['reddit']['cache_dir']}/password.cache")
            if not password_path.is_file():
                password_path.write_text(subprocess.run(
                    password_method[1], text=True, capture_output=True).stdout.strip())
            password = password_path.read_text()
        case "path":
            password = pathlib.PosixPath(os.path.expandvars(
                password_method[1])).read_text().strip()
        case "raw":
            password = password_method[1]
    return password



def prime_reddit(username: str, password: str, client_id: str) -> praw.Reddit:
    pass



if __name__ == "__main__":
    CONFIG = json.loads(pathlib.PosixPath(os.path.expandvars(
        "$XDG_CONFIG_HOME/eww/.config.json")).read_text())
    CONFIG["reddit"]["cache_dir"] = os.path.expandvars(
        CONFIG["reddit"]["cache_dir"])
    pathlib.PosixPath(CONFIG["reddit"]["cache_dir"]).mkdir(
        parents=True, exist_ok=True)
    print(get_reddit_password(CONFIG))

# vim:filetype=python
