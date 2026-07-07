"""
DayZRP Item Catalog Taxonomy

Mods provide the data.
DayZRP defines how the data is organized.
"""


CATEGORY_TREE = {
    "Weapons": [
        "Assault Rifles",
        "Battle Rifles",
        "Submachine Guns",
        "Pistols",
        "Revolvers",
        "DMRs",
        "Sniper Rifles",
        "Shotguns",
        "Machine Guns",
        "Launchers",
    ],

    "Attachments": [
        "Stocks",
        "Handguards",
        "Grips",
        "Optics",
        "Iron Sights",
        "Suppressors",
        "Muzzle Devices",
        "Flashlights",
        "Lasers",
        "Bipods",
    ],

    "Magazines": [
        "Rifle",
        "Pistol",
        "SMG",
        "DMR",
        "Sniper",
        "Shotgun",
        "Drum",
    ],

    "Ammunition": [
        "Rifle",
        "Intermediate",
        "Pistol",
        "Shotgun",
        "Sniper",
        "Explosive",
    ],

    "Medical": [
        "Bandages",
        "Pharmaceuticals",
        "IV Equipment",
        "Surgical",
        "Diagnostics",
        "Medical Tools",
    ],

    "Armor": [
        "Helmets",
        "Plate Carriers",
        "Chest Rigs",
        "Tactical Vests",
        "Holsters",
        "Pouches",
    ],

    "Clothing": [
        "Hats",
        "Facewear",
        "Eyewear",
        "Shirts",
        "Jackets",
        "Pants",
        "Gloves",
        "Footwear",
        "Belts",
        "Armbands",
        "NBC Equipment",
    ],

    "Equipment": [
        "Backpacks",
        "Containers",
        "Cases",
        "Radios",
        "Navigation",
        "Lighting",
        "Survival",
        "Filters",
    ],

    "Tools": [
        "Construction",
        "Repair",
        "Farming",
        "Fishing",
        "Electronics",
        "Utility",
    ],

    "Food & Drink": [
        "Food",
        "Drink",
        "Cooking",
        "Ingredients",
    ],

    "Crafting": [
        "Building Supplies",
        "Hardware",
        "Fabric",
        "Metal",
        "Plastic",
        "Chemicals",
    ],

    "Quest Items": [
        "Documents",
        "Keys",
        "Artifacts",
        "Evidence",
        "Currency",
        "Collectibles",
    ],

    "Miscellaneous": [],
}


WEAPON_FAMILIES = {
    # Assault Rifles
    "AK12": "Assault Rifles",
    "AK74": "Assault Rifles",
    "AK101": "Assault Rifles",
    "AKM": "Assault Rifles",
    "M4": "Assault Rifles",
    "HK416": "Assault Rifles",
    "SCARL": "Assault Rifles",
    "G36": "Assault Rifles",

    # Battle Rifles
    "FAL": "Battle Rifles",
    "SCARH": "Battle Rifles",
    "G3": "Battle Rifles",
    "HK417": "Battle Rifles",

    # SMGs
    "MP5": "Submachine Guns",
    "MP7": "Submachine Guns",
    "UMP": "Submachine Guns",
    "VECTOR": "Submachine Guns",

    # Pistols
    "GLOCK": "Pistols",
    "USP": "Pistols",
    "M9": "Pistols",
    "1911": "Pistols",

    # DMRs
    "SVD": "DMRs",
    "MK14": "DMRs",
    "M110": "DMRs",

    # Snipers
    "AWM": "Sniper Rifles",
    "M24": "Sniper Rifles",
    "L96": "Sniper Rifles",

    # Shotguns
    "M870": "Shotguns",
    "SAIGA": "Shotguns",

    # Machine Guns
    "PKM": "Machine Guns",
    "M249": "Machine Guns",
    "RPK": "Machine Guns",
}


def classify_weapon_family(classname):
    cls = classname.upper().replace("_", "")

    for family, subcategory in WEAPON_FAMILIES.items():
        if family in cls:
            return subcategory

    return "Firearms"


def classify_item(classname, display_name="", mod_name=""):
    cls = classname.lower()
    text = f"{classname} {display_name}".lower()
    mod = (mod_name or "").lower()

    # Additional Medical Supplies
    if cls.startswith("ams_"):

        if any(x in cls for x in ["gasmask", "nbc"]):
            if "filter" in cls:
                return "Equipment", "Filters"
            return "Clothing", "NBC Equipment"

        if any(x in cls for x in ["medchest", "firstaidkit", "mfak", "pouch"]):
            return "Equipment", "Containers"

        if any(x in cls for x in ["bandage", "bandaid", "tourniquet"]):
            return "Medical", "Bandages"

        if any(x in cls for x in [
            "aspirin",
            "methadone",
            "narcotics",
            "antisept",
            "vikasol",
            "poter",
            "polaris",
            "energy",
            "goldenstar",
            "pox",
            "ai2"
        ]):
            return "Medical", "Pharmaceuticals"

        if any(x in cls for x in ["splint", "absorbent", "bandagetape"]):
            return "Medical", "Medical Tools"

    if "waterstraw" in cls:
        return "Equipment", "Survival"

    if "heatpack" in cls:
        return "Equipment", "Survival"

    if "whistle" in cls:
        return "Tools", "Utility"

    return "Miscellaneous", "Unclassified"

    if "testkitreport" in cls:
        return "Medical", "Diagnostics"

        return "Miscellaneous", "Unclassified"

    # Attachments
    if any(x in cls for x in ["bttstock", "buttstock", "_stock", "magpul", "prs"]):
        return "Attachments", "Stocks"

    if any(x in cls for x in ["hndgrd", "handguard", "hng"]):
        return "Attachments", "Handguards"

    if any(x in cls for x in ["optic", "kobra", "acog", "elcan", "scope", "sight", "kashtan", "pso", "reflex", "lrhs"]):
        return "Attachments", "Optics"

    if any(x in cls for x in ["tlr", "tlrlight", "x300", "weaponlight"]):
        return "Attachments", "Flashlights"

    if any(x in cls for x in ["suppressor", "silencer"]):
        return "Attachments", "Suppressors"

    if any(x in cls for x in ["muzzle", "brake", "compensator"]):
        return "Attachments", "Muzzle Devices"

    if "bipod" in cls:
        return "Attachments", "Bipods"

    if any(x in cls for x in ["grip", "foregrip"]):
        return "Attachments", "Grips"

    # Magazines
    if cls.startswith("mag_") or "_mag_" in cls or any(x in cls for x in ["cmag", "stanag"]):
        return "Magazines", "Rifle"

    # Weapons
    if "ajw" in mod or cls.startswith("ajw"):
        return "Weapons", classify_weapon_family(classname)

    # General fallback
    if "ammo" in cls or "bullet" in cls or "round" in cls:
        return "Ammunition", "Rifle"
    
        return "Miscellaneous", "Unclassified"