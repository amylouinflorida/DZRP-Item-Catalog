from database import get_item_by_classname


def get_spawn_status(nominal):
    if nominal is None:
        return {
            "class": "spawn-unknown",
            "label": "Unknown",
            "tooltip": "No economy data has been imported."
        }

    if nominal == 0:
        return {
            "class": "spawn-disabled",
            "label": "Do Not Spawn",
            "tooltip": "This item is disabled in the DayZRP economy. Do not spawn it for players unless an Administrator has explicitly approved it."
        }

    return {
        "class": "spawn-active",
        "label": "Active Economy",
        "tooltip": "This item is currently enabled in the DayZRP economy."
    }


def decorate_item(item):

    item["spawn_status"] = get_spawn_status(
        item.get("nominal")
    )

    return item


def get_item(classname):

    item = get_item_by_classname(classname)

    if not item:
        return None

    return decorate_item(item)