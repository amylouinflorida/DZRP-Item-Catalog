import re
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

DB_PATH = Path("data/database/dayzrp_catalog.db")

TYPES_FILES = [
    "data/imports/ajw/types/AJ_Weapon_types.xml",
    "data/imports/ajw/types/AJ_WeaponMagazines_types.xml",
    "data/imports/ajw/types/AJ_Attachments_types.xml",
    "data/imports/ajw/types/AJ_Ammo_types.xml",
]

CONFIG_DIR = Path("data/imports/ajw/configs")


def connect_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def initialize_schema(conn):
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            classname TEXT UNIQUE NOT NULL,
            display_name TEXT,
            description TEXT,
            item_type TEXT,
            platform TEXT,
            mod_name TEXT DEFAULT 'AJW Weapons',
            weight INTEGER,
            size_x INTEGER,
            size_y INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS spawn_data (
            item_id INTEGER PRIMARY KEY,
            nominal INTEGER,
            min INTEGER,
            lifetime INTEGER,
            restock INTEGER,
            quantmin INTEGER,
            quantmax INTEGER,
            deloot INTEGER,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS item_usages (
            item_id INTEGER,
            usage TEXT,
            UNIQUE(item_id, usage)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS item_tiers (
            item_id INTEGER,
            tier TEXT,
            UNIQUE(item_id, tier)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS item_slots (
            item_id INTEGER,
            slot_name TEXT,
            direction TEXT,
            UNIQUE(item_id, slot_name, direction)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS item_magazines (
            weapon_id INTEGER,
            magazine_classname TEXT,
            UNIQUE(weapon_id, magazine_classname)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS item_ammo (
            weapon_id INTEGER,
            ammo_classname TEXT,
            UNIQUE(weapon_id, ammo_classname)
        )
    """)

    conn.commit()


def classify_item(classname):
    if classname.startswith("AJW_Mag_") or "_Mag_" in classname:
        return "Magazine"
    if classname.startswith("AJW_AmmoBox_"):
        return "Ammo Box"
    if classname.startswith("AJW_Ammo_"):
        return "Ammo"
    if classname.startswith("AJW_Optic_"):
        return "Optic"
    if classname.startswith("AJW_Magnifier_"):
        return "Magnifier"
    if "Suppressor" in classname:
        return "Suppressor"
    if "_HG" in classname or "Hndgrd" in classname:
        return "Handguard"
    if "_PG_" in classname or "_PGrip" in classname:
        return "Pistol Grip"
    if "_FG_" in classname:
        return "Foregrip"
    if "Bttstck" in classname or classname.startswith("AJW_BS_") or "_Stock_" in classname:
        return "Buttstock"
    if "_CH_" in classname:
        return "Charging Handle"
    if "_DC" in classname:
        return "Dust Cover"
    if "_MD_" in classname or "MuzzleBreak" in classname or "Comp" in classname:
        return "Muzzle Device"
    if "Bipod" in classname:
        return "Bipod"
    if "Laser" in classname or "PEQ" in classname or "DBAL" in classname or "NGAL" in classname or "MAWL" in classname:
        return "Laser"
    if "Gunlight" in classname or "Flashlight" in classname:
        return "Light"
    return "Weapon"


def infer_platform(classname):
    name = classname.replace("AJW_", "")

    known = [
        "AK74M", "AK105", "AK104", "AK103", "AK102", "AK101", "AKS74U",
        "M4A1", "HK416", "MCX", "SCARH", "SCARL", "SCAR", "ACR",
        "XM7", "SA58", "SVD", "SV98", "R700", "K98", "EVO3",
        "Vityaz", "PKM", "M60", "M82", "AWM", "DMK12", "MK12",
        "HKG28", "HoneyBadger", "Car15", "AK5C"
    ]

    for platform in known:
        if platform.lower() in name.lower():
            return platform

    if name.startswith("AK_"):
        return "AK"
    if name.startswith("M4_"):
        return "M4"
    if name.startswith("AR10_"):
        return "AR10"

    return None


def clean_display_name(classname):
    name = classname.replace("AJW_", "")
    name = name.replace("_", " ")
    name = name.replace("rnd", "Rnd")
    name = name.replace("FDE", "FDE")
    return name.strip()


def get_or_create_item(conn, classname):
    cur = conn.cursor()
    cur.execute("SELECT id FROM items WHERE classname = ?", (classname,))
    row = cur.fetchone()

    if row:
        return row[0]

    cur.execute("""
        INSERT INTO items (classname, display_name, item_type, platform)
        VALUES (?, ?, ?, ?)
    """, (
        classname,
        clean_display_name(classname),
        classify_item(classname),
        infer_platform(classname),
    ))

    conn.commit()
    return cur.lastrowid


def import_types_file(conn, path):
    tree = ET.parse(path)
    root = tree.getroot()

    for type_node in root.findall("type"):
        classname = type_node.attrib["name"]
        item_id = get_or_create_item(conn, classname)

        def text_int(tag, default=None):
            node = type_node.find(tag)
            return int(node.text) if node is not None and node.text else default

        flags = type_node.find("flags")
        deloot = int(flags.attrib.get("deloot", 0)) if flags is not None else 0

        conn.execute("""
            INSERT OR REPLACE INTO spawn_data
            (item_id, nominal, min, lifetime, restock, quantmin, quantmax, deloot)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id,
            text_int("nominal"),
            text_int("min"),
            text_int("lifetime"),
            text_int("restock"),
            text_int("quantmin"),
            text_int("quantmax"),
            deloot,
        ))

        for usage in type_node.findall("usage"):
            conn.execute(
                "INSERT OR IGNORE INTO item_usages (item_id, usage) VALUES (?, ?)",
                (item_id, usage.attrib["name"])
            )

        for value in type_node.findall("value"):
            conn.execute(
                "INSERT OR IGNORE INTO item_tiers (item_id, tier) VALUES (?, ?)",
                (item_id, value.attrib["name"])
            )

    conn.commit()


def extract_array(block, key):
    pattern = rf"{key}\[\]\s*=\s*\{{(.*?)\}};"
    match = re.search(pattern, block, re.DOTALL)
    if not match:
        return []

    raw = match.group(1)
    return re.findall(r'"([^"]+)"', raw)


def extract_scalar(block, key):
    match = re.search(rf'{key}\s*=\s*"([^"]*)";', block)
    return match.group(1) if match else None


def extract_int(block, key):
    match = re.search(rf"{key}\s*=\s*(\d+);", block)
    return int(match.group(1)) if match else None


def extract_item_size(block):
    match = re.search(r"itemSize\[\]\s*=\s*\{(\d+),\s*(\d+)\};", block)
    if not match:
        return None, None
    return int(match.group(1)), int(match.group(2))


def import_weapon_config(conn, path):
    text = Path(path).read_text(encoding="utf-8", errors="ignore")

    base_classes = re.finditer(
        r"class\s+(AJW_[A-Za-z0-9_]+_Base)\s*:\s*[A-Za-z0-9_]+\s*\{",
        text
    )

    for match in base_classes:
        class_name = match.group(1)
        start = match.end()
        end = text.find("\n\t};", start)
        if end == -1:
            continue

        block = text[start:end]

        display_name = extract_scalar(block, "displayName")
        description = extract_scalar(block, "descriptionShort")
        weight = extract_int(block, "weight")
        size_x, size_y = extract_item_size(block)

        attachments = extract_array(block, "attachments")
        magazines = extract_array(block, "magazines")
        ammo = extract_array(block, "chamberableFrom")

        # Find child weapon classes that inherit from this base.
        child_pattern = rf"class\s+(AJW_[A-Za-z0-9_]+)\s*:\s*{class_name}"
        child_classes = re.findall(child_pattern, text)

        if not child_classes:
            child_classes = [class_name]

        for weapon_class in child_classes:
            item_id = get_or_create_item(conn, weapon_class)

            conn.execute("""
                UPDATE items
                SET display_name = COALESCE(?, display_name),
                    description = COALESCE(?, description),
                    item_type = 'Weapon',
                    platform = COALESCE(platform, ?),
                    weight = COALESCE(?, weight),
                    size_x = COALESCE(?, size_x),
                    size_y = COALESCE(?, size_y)
                WHERE id = ?
            """, (
                display_name,
                description,
                infer_platform(weapon_class),
                weight,
                size_x,
                size_y,
                item_id,
            ))

            for slot in attachments:
                conn.execute("""
                    INSERT OR IGNORE INTO item_slots (item_id, slot_name, direction)
                    VALUES (?, ?, 'accepts')
                """, (item_id, slot))

            for mag in magazines:
                conn.execute("""
                    INSERT OR IGNORE INTO item_magazines (weapon_id, magazine_classname)
                    VALUES (?, ?)
                """, (item_id, mag))

            for ammo_class in ammo:
                conn.execute("""
                    INSERT OR IGNORE INTO item_ammo (weapon_id, ammo_classname)
                    VALUES (?, ?)
                """, (item_id, ammo_class))

    conn.commit()


def main():
    conn = connect_db()
    initialize_schema(conn)

    for path in TYPES_FILES:
        path_obj = Path(path)
        if path_obj.exists():
            print(f"Importing types: {path_obj}")
            import_types_file(conn, path_obj)

    if CONFIG_DIR.exists():
        for config_path in CONFIG_DIR.rglob("*.cpp"):
            print(f"Importing config: {config_path}")
            import_weapon_config(conn, config_path)

    conn.close()
    print("AJW import complete.")


if __name__ == "__main__":
    main()