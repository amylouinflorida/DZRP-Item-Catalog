import json
import re
from pathlib import Path
from pprint import pprint


AJW_ROOT = Path(r"D:\SteamLibrary\steamapps\common\DayZ\!Workshop\@AJs Weapons\addons")
OUTPUT_JSON = Path("data/imports/ajw_parsed_items.json")


TOP_LEVEL_MAP = {
    "AJW_Firearms_AssaultRifles": ("Weapons", "Assault Rifles"),
    "AJW_Firearms_Snipers": ("Weapons", "Sniper Rifles"),
    "AJW_Firearms_Rifles": ("Weapons", "Rifles"),
    "AJW_Firearms_SMG": ("Weapons", "SMGs"),
    "AJW_Firearms_LMG": ("Weapons", "LMGs"),
    "AJW_Firearms_Shotgun": ("Weapons", "Shotguns"),
    "AJW_Pistols": ("Weapons", "Pistols"),

    "AJW_Optics": ("Attachments", "Optics"),
    "AJW_Lasers": ("Attachments", "Lasers"),
    "AJW_Ammo": ("Ammunition", "Ammo"),
}


ATTACHMENT_SUBCATEGORY_MAP = {
    "Bipods": "Bipods",
    "BoltCarriers": "Bolt Carriers",
    "ChargingHandles": "Charging Handles",
    "DustCovers": "Dust Covers",
    "Extras": "Extras",
    "ForeGrips": "Foregrips",
    "HandGuard": "Handguards",
    "Lights": "Lights",
    "Magazines": "Magazines",
    "Magnifiers": "Magnifiers",
    "Muzzles": "Muzzles",
    "PistolGrips": "Pistol Grips",
    "Shared": "Shared",
    "Stocks": "Stocks",
    "Triggers": "Triggers",
}


def extract_string(text, field):
    match = re.search(rf'\b{field}\s*=\s*"([^"]*)"', text)
    return match.group(1).strip() if match else ""


def extract_number(text, field):
    match = re.search(rf'\b{field}\s*=\s*([0-9.]+)', text)
    return match.group(1).strip() if match else ""


def extract_array(text, field):
    match = re.search(rf'\b{field}\s*\[\]\s*=\s*\{{(.*?)\}};', text, re.DOTALL)
    if not match:
        return []

    body = match.group(1)

    quoted = re.findall(r'"([^"]+)"', body)
    if quoted:
        return [value.strip() for value in quoted if value.strip()]

    plain = re.findall(r'\b[A-Za-z0-9_]+\b', body)
    return [value.strip() for value in plain if value.strip()]


def extract_classnames(text):
    return re.findall(r'\bclass\s+([A-Za-z0-9_]+)\s*(?::|\{)', text)


def clean_description(description):
    if not description:
        return ""

    description = description.replace("\\n", " ")
    description = description.replace("\n", " ")
    description = re.sub(r"\s+", " ", description)

    return description.strip()


def prettify_folder(name):
    if not name:
        return ""

    name = name.replace("_", " ")
    name = re.sub(r"(?<!^)(?=[A-Z])", " ", name)
    return name.title()


def get_path_info(config_path):
    relative = config_path.relative_to(AJW_ROOT)
    parts = relative.parts

    top_folder = parts[0] if len(parts) > 0 else ""
    second_folder = parts[1] if len(parts) > 1 else ""
    third_folder = parts[2] if len(parts) > 2 else ""

    category, subcategory = TOP_LEVEL_MAP.get(top_folder, ("Miscellaneous", prettify_folder(top_folder)))

    family = ""

    if top_folder == "AJW_Attachments":
        category = "Attachments"
        subcategory = ATTACHMENT_SUBCATEGORY_MAP.get(second_folder, prettify_folder(second_folder))
        family = third_folder or second_folder

    elif top_folder in TOP_LEVEL_MAP:
        family = second_folder

    else:
        family = second_folder or third_folder

    return {
        "source_file": str(relative),
        "source_path": list(parts[:-1]),
        "top_folder": top_folder,
        "category": category,
        "subcategory": subcategory,
        "family": family,
    }


def pick_main_class(classes):
    ignored = {
        "CfgPatches",
        "CfgWeapons",
        "CfgMagazines",
        "CfgVehicles",
        "CfgNonAIVehicles",
        "CfgAmmo",
        "DamageSystem",
        "GlobalHealth",
        "Health",
        "Shock",
        "Blood",
        "Particles",
        "OpticsInfo",
        "SemiAuto",
        "FullAuto",
        "Single",
        "NoiseShot",
        "OnFire",
        "SmokeCloud",
        "MuzzleFlash",
        "Overheating",
        "SmokingBarrel1",
        "OpenChamberSmoke",
        "OnBulletCasingEject",
        "ChamberSmokeRaise",
    }

    real_classes = [c for c in classes if c not in ignored]

    for classname in reversed(real_classes):
        if classname.startswith("AJW_") and "Base" not in classname and "Proxy" not in classname:
            return classname

    for classname in reversed(real_classes):
        if "Base" not in classname and "Proxy" not in classname:
            return classname

    return real_classes[-1] if real_classes else ""


def detect_item_type(path_info):
    category = path_info["category"]
    subcategory = path_info["subcategory"]

    if category == "Weapons":
        return "Weapon"

    if category == "Ammunition":
        return "Ammunition"

    if category == "Attachments":
        if subcategory == "Magazines":
            return "Magazine"
        return "Attachment"

    return "Item"


def parse_config(config_path):
    text = config_path.read_text(encoding="utf-8", errors="ignore")

    classes = extract_classnames(text)
    path_info = get_path_info(config_path)

    item = {
        **path_info,

        "classname": pick_main_class(classes),
        "display_name": extract_string(text, "displayName"),
        "description": clean_description(extract_string(text, "descriptionShort")),
        "model": extract_string(text, "model"),

        "item_type": detect_item_type(path_info),

        "attachments": extract_array(text, "attachments"),
        "magazines": extract_array(text, "magazines"),
        "chamberable_from": extract_array(text, "chamberableFrom"),

        "item_size": extract_array(text, "itemSize"),
        "inventory_slot": extract_array(text, "inventorySlot"),
        "weight": extract_number(text, "weight"),

        "repairable_with_kits": extract_array(text, "repairableWithKits"),
        "repair_costs": extract_array(text, "repairCosts"),

        "hidden_selections": extract_array(text, "hiddenSelections"),
        "hidden_selection_textures": extract_array(text, "hiddenSelectionsTextures"),

        "classes_found": classes,
    }

    return item


def main():
    print("=" * 80)
    print("AJW Parser v1 Starting")
    print("=" * 80)

    print("AJW root:", AJW_ROOT)
    print("Root exists:", AJW_ROOT.exists())

    configs = list(AJW_ROOT.rglob("config.cpp"))
    print("Configs found:", len(configs))

    if not configs:
        print("No config.cpp files found. Check AJW_ROOT.")
        return

    items = []

    for config in configs:
        try:
            item = parse_config(config)
            items.append(item)
        except Exception as error:
            print("ERROR:", config)
            print(error)

    print("\nParsed items:", len(items))

    type_counts = {}
    category_counts = {}

    for item in items:
        type_counts[item["item_type"]] = type_counts.get(item["item_type"], 0) + 1
        key = f"{item['category']} / {item['subcategory']}"
        category_counts[key] = category_counts.get(key, 0) + 1

    print("\nItem types:")
    for key, value in sorted(type_counts.items()):
        print(f"  {key}: {value}")

    print("\nCategories:")
    for key, value in sorted(category_counts.items()):
        print(f"  {key}: {value}")

    print("\nSample item:")
    pprint(items[0], width=140)

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_JSON.open("w", encoding="utf-8") as file:
        json.dump(items, file, indent=2, ensure_ascii=False)

    print(f"\nSaved parsed data to: {OUTPUT_JSON}")
    print("Done.")


if __name__ == "__main__":
    main()