import utils


def redir_to_handlers(formats, dunst_envs: dict) -> str:
    if utils.contains_pango(dunst_envs["DUNST_BODY"]):
        dunst_envs["DUNST_BODY"] = utils.strip_pango_tags(dunst_envs["DUNST_BODY"])
    if utils.contains_pango(dunst_envs["DUNST_SUMMARY"]):
        dunst_envs["DUNST_SUMMARY"] = utils.strip_pango_tags(
            dunst_envs["DUNST_SUMMARY"]
        )

    dunst_envs["SUMMARY_LIMITER"] = ""
    summary_lang_char_check = utils.has_non_english_chars(
        dunst_envs["DUNST_SUMMARY"][:15]
    )
    if summary_lang_char_check["CJK"]:
        dunst_envs["SUMMARY_LIMITER"] = 14
    elif summary_lang_char_check["CYR"]:
        dunst_envs["SUMMARY_LIMITER"] = 30

    dunst_envs["BODY_LIMITER"] = ""
    body_lang_char_check = utils.has_non_english_chars(dunst_envs["DUNST_BODY"][:70])
    if body_lang_char_check["CJK"]:
        dunst_envs["BODY_LIMITER"] = 80
    elif body_lang_char_check["CYR"]:
        dunst_envs["BODY_LIMITER"] = 110
    else:
        dunst_envs["BODY_LIMITER"] = 100

    match dunst_envs["DUNST_APP_NAME"]:
        case "notify-send":
            return notify_send_handler(formats, dunst_envs)
        case "volume":
            return volume_handler(formats, dunst_envs)
        case "brightness":
            return brightness_handler(formats, dunst_envs)
        case "shot":
            return shot_handler(formats, dunst_envs)
        case "todo":
            return todo_handler(formats, dunst_envs)
        case _:
            return default_handler(formats, dunst_envs)


def shot_handler(formats, attributes: dict) -> str:
    # TODO: Make this better
    attributes["DELETE"] = f"rm --force \\'{attributes['DUNST_ICON_PATH']}\\'"
    attributes["OPEN"] = f"xdg-open \\'{attributes['DUNST_ICON_PATH']}\\'"
    attributes["DUNST_APP_NAME"] = utils.prettify_name(attributes["DUNST_APP_NAME"])
    return formats["shot"] % attributes


def default_handler(formats, attributes: dict) -> str:
    attributes["DUNST_APP_NAME"] = utils.prettify_name(attributes["DUNST_APP_NAME"])
    return formats["default"] % attributes


def notify_send_handler(formats, attributes: dict) -> str:
    attributes["DUNST_APP_NAME"] = utils.prettify_name(attributes["DUNST_APP_NAME"])
    return formats["notify-send"] % attributes


def brightness_handler(formats, attributes: dict) -> str:
    attributes["DUNST_APP_NAME"] = utils.prettify_name(attributes["DUNST_APP_NAME"])
    return formats["brightness"] % attributes


def volume_handler(formats, attributes: dict) -> str:
    attributes["DUNST_APP_NAME"] = utils.prettify_name(attributes["DUNST_APP_NAME"])
    return formats["volume"] % attributes


def todo_handler(formats, attributes: dict) -> str:
    splitted = attributes["DUNST_BODY"].split(" ")
    attributes["TOTAL"] = int(splitted[4])
    attributes["DONE"] = int(splitted[0])
    attributes["PERC"] = (attributes["DONE"] / attributes["TOTAL"]) * 100
    attributes["DUNST_APP_NAME"] = utils.prettify_name(attributes["DUNST_APP_NAME"])
    return formats["todo"] % attributes


def shot_icon_handler(formats, attributes: dict) -> str:
    attributes["DUNST_APP_NAME"] = utils.prettify_name(attributes["DUNST_APP_NAME"])
    return formats["shot_icon"] % attributes


# vim:filetype=python
