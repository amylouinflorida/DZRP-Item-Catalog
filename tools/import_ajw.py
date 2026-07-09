import json
import sqlite3
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from tools.ajw_parser_v1 import AJW_ROOT, parse_config


DB_PATH = ROOT_DIR / "data" / "database" / "dayzrp_catalog.db"


def ensure_columns(cursor):
    columns = [row[1] for row in cursor.execute("PRAGMA table_info(items)").fetchall()]

    needed = {
        "item_type": "TEXT",
        "model": "TEXT",
        "source_file": "TEXT",
        "family": "TEXT",
        "weight": "TEXT",
        "item_size": "TEXT",
    }

    for column, col_type in needed.items():
        if column not in columns:
            print(f"Adding column: items.{column}")
            cursor.execute(f"ALTER TABLE items ADD COLUMN {column} {col_type}")


def get_or_create_mod(cursor):
    cursor.execute("""
        INSERT OR IGNORE INTO mods (name, author, type, description)
        VALUES (?, ?, ?, ?)
    """, (
        "AJW Weapons",
        "AJ",
        "Weapon Mod",
        "Imported automatically from extracted AJW config.cpp files."
    ))

    cursor.execute("SELECT id FROM mods WHERE name = ?", ("AJW Weapons",))
    return cursor.fetchone()[0]


def upsert_item(cursor, item, mod_id):
    cursor.execute("""
        INSERT INTO items (
            classname,
            display_name,
            description,
            category,
            subcategory,
            mod_id,
            item_type,
            model,
            source_file,
            family,
            weight,
            item_size
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(classname) DO UPDATE SET
            display_name = excluded.display_name,
            description = excluded.description,
            category = excluded.category,
            subcategory = excluded.subcategory,
            mod_id = excluded.mod_id,
            item_type = excluded.item_type,
            model = excluded.model,
            source_file = excluded.source_file,
            family = excluded.family,
            weight = excluded.weight,
            item_size = excluded.item_size
    """, (
        item["classname"],
        item["display_name"] or item["classname"],
        item["description"],
        item["category"],
        item["subcategory"],
        mod_id,
        item["item_type"],
        item["model"],
        item["source_file"],
        item["family"],
        item["weight"],
        json.dumps(item["item_size"]),
    ))


def main():
    print("=" * 80)
    print("AJW Database Import Starting")
    print("=" * 80)

    print("DB:", DB_PATH)
    print("DB exists:", DB_PATH.exists())
    print("AJW root:", AJW_ROOT)
    print("AJW root exists:", AJW_ROOT.exists())

    configs = list(AJW_ROOT.rglob("config.cpp"))
    print("Configs found:", len(configs))

    if not configs:
        print("No configs found. Stopping.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    ensure_columns(cursor)
    mod_id = get_or_create_mod(cursor)

    imported = 0
    skipped = 0
    counts = {}

    for config in configs:
        item = parse_config(config)

        if not item["classname"]:
            skipped += 1
            continue

        upsert_item(cursor, item, mod_id)

        imported += 1
        key = f"{item['category']} / {item['subcategory']}"
        counts[key] = counts.get(key, 0) + 1

    conn.commit()
    conn.close()

    print("\nImported:", imported)
    print("Skipped:", skipped)

    print("\nCategory Counts:")
    for key, value in sorted(counts.items()):
        print(f"  {key}: {value}")

    print("\nDone.")


if __name__ == "__main__":
    main()
