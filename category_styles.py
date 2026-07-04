CATEGORY_STYLES = {
    "Medical": {
        "icon": "fa-solid fa-kit-medical",
        "class": "category-medical",
        "subtitle": "Healing supplies, medicine, and trauma care."
    },
    "Clothing": {
        "icon": "fa-solid fa-shirt",
        "class": "category-clothing",
        "subtitle": "Wearable equipment, armor, and apparel."
    },
    "Weapons": {
        "icon": "fa-solid fa-gun",
        "class": "category-weapons",
        "subtitle": "Firearms, melee weapons, and combat gear."
    },
    "Food": {
        "icon": "fa-solid fa-drumstick-bite",
        "class": "category-food",
        "subtitle": "Food, canned goods, and survival nutrition."
    },
    "Tools": {
        "icon": "fa-solid fa-screwdriver-wrench",
        "class": "category-tools",
        "subtitle": "Repair tools, crafting tools, and utility items."
    },
    "Survival": {
        "icon": "fa-solid fa-campground",
        "class": "category-survival",
        "subtitle": "Survival gear, wilderness tools, and field equipment."
    },
    "Building": {
        "icon": "fa-solid fa-hammer",
        "class": "category-building",
        "subtitle": "Building supplies, kits, and construction tools."
    },
    "Vehicles": {
        "icon": "fa-solid fa-car-side",
        "class": "category-vehicles",
        "subtitle": "Vehicles, parts, boats, and transport equipment."
    },
    "Miscellaneous": {
        "icon": "fa-solid fa-cube",
        "class": "category-misc",
        "subtitle": "Other cataloged assets and uncategorized content."
    }
}


DEFAULT_CATEGORY_STYLE = {
    "icon": "fa-solid fa-box",
    "class": "category-default",
    "subtitle": "Cataloged DayZRP assets."
}


def get_category_style(category):
    return CATEGORY_STYLES.get(category, DEFAULT_CATEGORY_STYLE)