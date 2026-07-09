import json
import sqlite3
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from tools.ajw_parser_v1 import AJW_ROOT, parse_config

DB_PATH = ROOT_DIR / "data" / "database" / "dayzrp_catalog.db"


def ensure_tables(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS item_slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        classname TEXT NOT NULL,
        slot_name TEXT NOT NULL,
        slot_role TEXT NOT NULL,
        source TEXT,
        UNIQUE(classname, slot_name, slot_role)
    )
""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS item_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_classname TEXT NOT NULL,
            slot_name TEXT NOT NULL,
            slot_role TEXT NOT NULL,
            source TEXT,
            UNIQUE(item_classname, slot_name, slot_role)
        )
    """)


def guess_slot_group(slot_name):
    s = slot_name.lower()

    if "optic" in s:
        return "Optics"
    if "magnifier" in s:
        return "Magnifiers"
    if "muzzle" in s or "suppressor" in s:
        return "Muzzles"
    if "flashlight" in s or "light" in s:
        return "Lights"
    if "laser" in s:
        return "Lasers"
    if "stock" in s or "buttstock" in s:
        return "Stocks"
    if "handguard" in s or "hndgrd" in s:
        return "Handguards"
    if "foregrip" in s or "_fg" in s:
        return "Foregrips"
    if "pistolgrip" in s or "_pg" in s:
        return "Pistol Grips"
    if "trigger" in s:
        return "Triggers"
    if "magazine" in s:
        return "Magazines"

    return "Other"


def save_slot(cursor, slot_name):
    cursor.execute("""
        INSERT OR IGNORE INTO compatibility_slots (slot_name, slot_group)
        VALUES (?, ?)
    """, (slot_name, guess_slot_group(slot_name)))


def save_item_slot(cursor, classname, slot_name, role, source_file):
    save_slot(cursor, slot_name)

    cursor.execute("SELECT id FROM items WHERE classname = ?", (classname,))
    row = cursor.fetchone()

    if not row:
        print(f"  ⚠ Item not in items table yet, skipping slot: {classname}")
        return

    item_id = row[0]

    cursor.execute("""
        INSERT OR IGNORE INTO item_slots (
            item_id,
            slot_name,
            direction
        )
        VALUES (?, ?, ?)
    """, (
        item_id,
        slot_name,
        role
    ))


def main():
    print("=" * 80)
    print("AJW Slot Import Starting")
    print("=" * 80)

    print("Database:", DB_PATH)
    print("DB exists:", DB_PATH.exists())
    print("AJW root:", AJW_ROOT)
    print("AJW root exists:", AJW_ROOT.exists())

    configs = list(AJW_ROOT.rglob("config.cpp"))
    print("Configs found:", len(configs))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    ensure_tables(cursor)

    accepted_count = 0
    used_count = 0
    skipped = 0

    for index, config in enumerate(configs, start=1):
        item = parse_config(config)

        classname = item.get("classname", "")
        if not classname:
            skipped += 1
            continue

        print("-" * 80)
        print(f"[{index}/{len(configs)}] {classname}")
        print(f"  Name: {item.get('display_name')}")
        print(f"  Type: {item.get('item_type')}")
        print(f"  Category: {item.get('category')} / {item.get('subcategory')}")

        # Weapons ACCEPT attachment slots.
        for slot in item.get("attachments", []):
            print(f"  ACCEPTS SLOT: {slot}")
            save_item_slot(cursor, classname, slot, "accepts", item["source_file"])
            accepted_count += 1

        # Attachments/Magazines/other assets USE inventory slots.
        # This is how we later connect attachments to weapons.
        for slot in item.get("inventory_slot", []):
            print(f"  USES SLOT: {slot}")
            save_item_slot(cursor, classname, slot, "uses", item["source_file"])
            used_count += 1

    conn.commit()

    print("\n" + "=" * 80)
    print("SLOT IMPORT COMPLETE")
    print("=" * 80)
    print("Accepted slots imported:", accepted_count)
    print("Used slots imported:", used_count)
    print("Skipped:", skipped)

    slot_total = cursor.execute("SELECT COUNT(*) FROM compatibility_slots").fetchone()[0]
    item_slot_total = cursor.execute("SELECT COUNT(*) FROM item_slots").fetchone()[0]

    print("Total compatibility slots:", slot_total)
    print("Total item-slot links:", item_slot_total)

    conn.close()


if __name__ == "__main__":
    main()