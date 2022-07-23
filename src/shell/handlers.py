import datetime
import utils
import cache

def redir_to_handlers(formats, attributes: dict) -> str:
    attributes["TIMESTAMP"] = datetime.datetime.now().strftime(attributes["TIMESTAMP_FORMAT"])

    match attributes["urgency"]:
        case cache.Urgency.LOW:
            attributes["URGENCY"] = "LOW"
        case cache.Urgency.NORMAL:
            attributes["URGENCY"] = "NORMAL"
        case cache.Urgency.CRITICAL:
            attributes["URGENCY"] = "CRITICAL"
        case _:
            attributes["URGENCY"] = "NORMAL"

    if utils.contains_pango(attributes["body"]):
        attributes["body"] = utils.strip_pango_tags(attributes["body"])
    if utils.contains_pango(attributes["summary"]):
        attributes["summary"] = utils.strip_pango_tags(
            attributes["summary"]
        )

    if "'" in attributes["body"]:
        attributes["body"] = attributes["body"].replace("'", "\\'")
    if "'" in attributes["summary"]:
        attributes["summary"] = attributes["summary"].replace("'", "\\'")

    attributes["SUMMARY_LIMITER"] = ""
    summary_lang_char_check = utils.has_non_english_chars(
        attributes["summary"][:15]
    )
    if summary_lang_char_check["CJK"]:
        attributes["SUMMARY_LIMITER"] = 14
    elif summary_lang_char_check["CYR"]:
        attributes["SUMMARY_LIMITER"] = 30

    attributes["BODY_LIMITER"] = ""
    body_lang_char_check = utils.has_non_english_chars(attributes["body"][:70])
    if body_lang_char_check["CJK"]:
        attributes["BODY_LIMITER"] = 80
    elif body_lang_char_check["CYR"]:
        attributes["BODY_LIMITER"] = 110
    else:
        attributes["BODY_LIMITER"] = 100

    match attributes["appname"]:
        case "notify-send":
            return notify_send_handler(formats, attributes)
        case "volume":
            return volume_handler(formats, attributes)
        case "brightness":
            return brightness_handler(formats, attributes)
        case "shot":
            return shot_handler(formats, attributes)
        case "shot_icon":
            return shot_icon_handler(formats, attributes)
        case "todo":
            return todo_handler(formats, attributes)
        case "Spotify":
            return Spotify_handler(formats, attributes)
        case _:
            return default_handler(formats, attributes)


def shot_handler(formats, attributes: dict) -> str:
    # TODO: Make this better
    attributes["DELETE"] = f"rm --force \\'{attributes['iconpath']}\\'"
    attributes["OPEN"] = f"xdg-open \\'{attributes['iconpath']}\\'"
    attributes["appname"] = utils.prettify_name(attributes["appname"])
    return formats["shot"] % attributes


def Spotify_handler(formats, attributes: dict) -> str:
    return formats["Spotify"] % attributes


def default_handler(formats, attributes: dict) -> str:
    attributes["appname"] = utils.prettify_name(attributes["appname"])
    return formats["default"] % attributes


def notify_send_handler(formats, attributes: dict) -> str:
    attributes["appname"] = utils.prettify_name(attributes["appname"])
    return formats["notify-send"] % attributes


def brightness_handler(formats, attributes: dict) -> str:
    attributes["appname"] = utils.prettify_name(attributes["appname"])
    return formats["brightness"] % attributes


def volume_handler(formats, attributes: dict) -> str:
    attributes["appname"] = utils.prettify_name(attributes["appname"])
    return formats["volume"] % attributes


def todo_handler(formats, attributes: dict) -> str:
    splitted = attributes["body"].split(" ")
    attributes["TOTAL"] = int(splitted[4])
    attributes["DONE"] = int(splitted[0])
    attributes["PERC"] = (attributes["DONE"] / attributes["TOTAL"]) * 100
    attributes["appname"] = utils.prettify_name(attributes["appname"])
    return formats["todo"] % attributes


def shot_icon_handler(formats, attributes: dict) -> str:
    attributes["appname"] = utils.prettify_name(attributes["appname"])
    return formats["shot_icon"] % attributes


# vim:filetype=python
