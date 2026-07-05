import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

DB_PATH = Path("data/database/dayzrp_catalog.db")

TYPE_FILES = [
    Path("data/imports/ajw/types/AJ_Weapon_types.xml"),
    Path("data/imports/ajw/types/AJ_WeaponMagazines_types.xml"),
    Path("data/imports/ajw/types/AJ_Attachments_types.xml"),
    Path("data/imports/ajw/types/AJ_Ammo_types.xml"),
]


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
    if classname.startswith("AJW_BS_") or "Bttstck" in classname or "_Stock_" in classname:
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


def clean_display_name(classname):
    return classname.replace("AJW_", "").replace("_", " ").strip()


def ensure_columns(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(items)")
    existing = [row[1] for row in cur.fetchall()]

    columns = {
        "item_type": "TEXT",
        "platform": "TEXT",
        "weight": "INTEGER",
        "size_x": "INTEGER",
        "size_y": "INTEGER",
    }

    for column, definition in columns.items():
        if column not in existing:
            cur.execute(f"ALTER TABLE items ADD COLUMN {column} {definition}")
            print(f"Added column: items.{column}")

    conn.commit()


def ensure_support_tables(conn):
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS spawn_data (
            item_id INTEGER PRIMARY KEY,
            nominal INTEGER,
            min INTEGER,
            lifetime INTEGER,
            restock INTEGER,
            quantmin INTEGER,
            quantmax INTEGER,
            deloot INTEGER
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

    conn.commit()


def get_or_create_item(conn, classname):
    cur = conn.cursor()

    cur.execute("SELECT id FROM items WHERE classname = ?", (classname,))
    row = cur.fetchone()

    if row:
        item_id = row[0]
        cur.execute("""
            UPDATE items
            SET item_type = COALESCE(item_type, ?),
                display_name = COALESCE(display_name, ?)
            WHERE id = ?
        """, (classify_item(classname), clean_display_name(classname), item_id))
        return item_id

    cur.execute("""
        INSERT INTO items (classname, display_name, item_type)
        VALUES (?, ?, ?)
    """, (classname, clean_display_name(classname), classify_item(classname)))

    return cur.lastrowid


def get_int(node, tag):
    child = node.find(tag)
    if child is None or child.text is None:
        return None
    try:
        return int(child.text)
    except ValueError:
        return None


def import_type_file(conn, path):
    if not path.exists():
        print(f"Missing file: {path}")
        return 0

    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        print(f"Empty file: {path}")
        return 0

    root = ET.fromstring(text)
    type_nodes = root.findall(".//type")

    print(f"{path.name}: found {len(type_nodes)} items")

    imported = 0

    for type_node in type_nodes:
        classname = type_node.attrib.get("name")
        if not classname:
            continue

        item_id = get_or_create_item(conn, classname)

        flags = type_node.find("flags")
        deloot = 0
        if flags is not None:
            deloot = int(flags.attrib.get("deloot", 0))

        conn.execute("""
            INSERT OR REPLACE INTO spawn_data
            (item_id, nominal, min, lifetime, restock, quantmin, quantmax, deloot)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id,
            get_int(type_node, "nominal"),
            get_int(type_node, "min"),
            get_int(type_node, "lifetime"),
            get_int(type_node, "restock"),
            get_int(type_node, "quantmin"),
            get_int(type_node, "quantmax"),
            deloot,
        ))

        for usage in type_node.findall("usage"):
            conn.execute("""
                INSERT OR IGNORE INTO item_usages (item_id, usage)
                VALUES (?, ?)
            """, (item_id, usage.attrib.get("name")))

        for value in type_node.findall("value"):
            conn.execute("""
                INSERT OR IGNORE INTO item_tiers (item_id, tier)
                VALUES (?, ?)
            """, (item_id, value.attrib.get("name")))

        imported += 1

    conn.commit()
    return imported


def main():
    print("Database:", DB_PATH.resolve())

    conn = sqlite3.connect(DB_PATH)

    ensure_columns(conn)
    ensure_support_tables(conn)

    total = 0
    for path in TYPE_FILES:
        total += import_type_file(conn, path)

    conn.close()

    print(f"Import complete. Imported/updated {total} XML items.")


if __name__ == "__main__":
    main()