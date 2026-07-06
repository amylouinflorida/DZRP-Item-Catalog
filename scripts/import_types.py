import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from services.classification_service import classify_item

DB_PATH = Path("data/database/dayzrp_catalog.db")

MOD_NAME = "AJW Weapons"
MOD_AUTHOR = "AJ45"
MOD_TYPE = "Weapons"
MOD_LOGO = "ajw-weapons.png"
MOD_WEBSITE = "https://steamcommunity.com/sharedfiles/filedetails/?id=3571685323"
MOD_DESCRIPTION = "AJW Weapons imported from DayZRP server economy files."

TYPE_FILES = [
    Path("data/imports/ajw/types/types.xml")
]

def classify_category(classname):
    if classname.startswith("AJW_"):
        return "Weapons"
    return "Uncategorized"


def classify_subcategory(classname):
    if classname.startswith("AJW_Mag_") or "_Mag_" in classname:
        return "Magazine"
    if classname.startswith("AJW_AmmoBox_"):
        return "Ammo Box"
    if classname.startswith("AJW_Ammo_"):
        return "Ammo"
    if classname.startswith("AJW_Optic_"):
        return "Attachment"
    if classname.startswith("AJW_Magnifier_"):
        return "Attachment"
    if "Suppressor" in classname:
        return "Attachment"
    if "_HG" in classname or "Hndgrd" in classname:
        return "Attachment"
    if "_PG_" in classname or "_PGrip" in classname:
        return "Attachment"
    if "_FG_" in classname:
        return "Attachment"
    if classname.startswith("AJW_BS_") or "Bttstck" in classname or "_Stock_" in classname:
        return "Attachment"
    if "_CH_" in classname:
        return "Attachment"
    if "_DC" in classname:
        return "Attachment"
    if "_MD_" in classname or "MuzzleBreak" in classname or "Comp" in classname:
        return "Attachment"
    if "Bipod" in classname:
        return "Attachment"
    if "Laser" in classname or "PEQ" in classname or "DBAL" in classname or "NGAL" in classname or "MAWL" in classname:
        return "Attachment"
    if "Gunlight" in classname or "Flashlight" in classname:
        return "Attachment"
    return "Weapon"


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
        "spawn_status": "TEXT",
    }

    for column, definition in columns.items():
        if column not in existing:
            cur.execute(f"ALTER TABLE items ADD COLUMN {column} {definition}")
            print(f"Added column: items.{column}")

    conn.commit()


def ensure_tables(conn):
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
            deloot INTEGER,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS item_usages (
            item_id INTEGER,
            usage TEXT,
            UNIQUE(item_id, usage),
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS item_tiers (
            item_id INTEGER,
            tier TEXT,
            UNIQUE(item_id, tier),
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)

    conn.commit()


def get_or_create_mod(conn):
    cur = conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO mods (name, author, type, logo, website, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        MOD_NAME,
        MOD_AUTHOR,
        MOD_TYPE,
        MOD_LOGO,
        MOD_WEBSITE,
        MOD_DESCRIPTION,
    ))

    cur.execute("""
        UPDATE mods
        SET author = ?, type = ?, logo = ?, website = ?, description = ?
        WHERE name = ?
    """, (
        MOD_AUTHOR,
        MOD_TYPE,
        MOD_LOGO,
        MOD_WEBSITE,
        MOD_DESCRIPTION,
        MOD_NAME,
    ))

    cur.execute("SELECT id FROM mods WHERE name = ?", (MOD_NAME,))
    mod_id = cur.fetchone()[0]

    conn.commit()
    return mod_id


def get_or_create_item(conn, classname, mod_id):
    cur = conn.cursor()

    cur.execute("SELECT id FROM items WHERE classname = ?", (classname,))
    row = cur.fetchone()

    category, subcategory, item_type = classify_item(classname)
    display_name = clean_display_name(classname)

    if row:
        item_id = row[0]

        cur.execute("""
            UPDATE items
            SET item_type = ?,
                display_name = COALESCE(NULLIF(display_name, ''), ?),
                category = ?,
                subcategory = ?,
                mod_id = COALESCE(mod_id, ?)
            WHERE id = ?
        """, (
            item_type,
            display_name,
            category,
            subcategory,
            mod_id,
            item_id,
        ))

        return item_id

    cur.execute("""
        INSERT INTO items (classname, display_name, category, subcategory, item_type, mod_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        classname,
        display_name,
        category,
        subcategory,
        item_type,
        mod_id,
    ))

    return cur.lastrowid


def get_int(type_node, tag):
    child = type_node.find(tag)

    if child is None or child.text is None:
        return None

    try:
        return int(child.text)
    except ValueError:
        return None


def import_type_file(conn, path, mod_id):
    if not path.exists():
        print(f"Missing file: {path}")
        return 0

    if path.stat().st_size == 0:
        print(f"Empty file: {path}")
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

        item_id = get_or_create_item(conn, classname, mod_id)

        flags = type_node.find("flags")
        deloot = 0

        if flags is not None:
            deloot = int(flags.attrib.get("deloot", 0))

        nominal = get_int(type_node, "nominal")
        spawn_status = "disabled" if nominal == 0 else "active"

        conn.execute("""
            INSERT OR REPLACE INTO spawn_data
            (item_id, nominal, min, lifetime, restock, quantmin, quantmax, deloot)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id,
            nominal,
            get_int(type_node, "min"),
            get_int(type_node, "lifetime"),
            get_int(type_node, "restock"),
            get_int(type_node, "quantmin"),
            get_int(type_node, "quantmax"),
            deloot,
        ))

        conn.execute("""
            UPDATE items
            SET spawn_status = ?
            WHERE id = ?
        """, (
            spawn_status,
            item_id,
        ))

        for usage in type_node.findall("usage"):
            usage_name = usage.attrib.get("name")
            if usage_name:
                conn.execute("""
                    INSERT OR IGNORE INTO item_usages (item_id, usage)
                    VALUES (?, ?)
                """, (item_id, usage_name))

        for value in type_node.findall("value"):
            tier_name = value.attrib.get("name")
            if tier_name:
                conn.execute("""
                    INSERT OR IGNORE INTO item_tiers (item_id, tier)
                    VALUES (?, ?)
                """, (item_id, tier_name))

        imported += 1

    conn.commit()
    return imported


def main():
    print("Database:", DB_PATH.resolve())

    conn = sqlite3.connect(DB_PATH)

    ensure_columns(conn)
    ensure_tables(conn)

    mod_id = get_or_create_mod(conn)

    print("\nTYPE FILES BEING CHECKED:")
    for file in TYPE_FILES:
        print(
            file.resolve(),
            "exists:",
            file.exists(),
            "size:",
            file.stat().st_size if file.exists() else "missing"
        )

    total = 0

    for path in TYPE_FILES:
        total += import_type_file(conn, path, mod_id)

    conn.close()

    print(f"\nImport complete. Imported/updated {total} XML items.")


if __name__ == "__main__":
    main()