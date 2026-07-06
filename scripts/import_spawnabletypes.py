import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

DB_PATH = Path("data/database/dayzrp_catalog.db")
SPAWNABLE_FILE = Path("data/imports/ajw/types/spawnabletypes.xml")


def get_or_create_item(conn, classname):
    cur = conn.cursor()

    cur.execute("SELECT id FROM items WHERE classname = ?", (classname,))
    row = cur.fetchone()

    if row:
        return row[0]

    cur.execute("""
        INSERT INTO items (classname, display_name, category, subcategory, item_type)
        VALUES (?, ?, ?, ?, ?)
    """, (
        classname,
        classname.replace("_", " "),
        "Miscellaneous",
        "Miscellaneous",
        "Unknown"
    ))

    return cur.lastrowid


def main():
    conn = sqlite3.connect(DB_PATH)

    if not SPAWNABLE_FILE.exists():
        print("Missing spawnabletypes.xml")
        return

    root = ET.parse(SPAWNABLE_FILE).getroot()

    imported = 0

    for type_node in root.findall(".//type"):
        weapon_classname = type_node.attrib.get("name")
        if not weapon_classname:
            continue

        weapon_id = get_or_create_item(conn, weapon_classname)

        for attachment_group in type_node.findall("attachments"):
            group_chance = float(attachment_group.attrib.get("chance", 1.0))

            for item_node in attachment_group.findall("item"):
                attached_classname = item_node.attrib.get("name")
                if not attached_classname:
                    continue

                item_chance = float(item_node.attrib.get("chance", 1.0))
                final_chance = group_chance * item_chance

                attached_id = get_or_create_item(conn, attached_classname)

                conn.execute("""
                    INSERT OR REPLACE INTO item_relationships
                    (source_item_id, target_item_id, relationship_type, chance, notes)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    weapon_id,
                    attached_id,
                    "spawns_with",
                    final_chance,
                    "Imported from spawnabletypes.xml"
                ))

                imported += 1

    conn.commit()
    conn.close()

    print(f"Imported {imported} spawn relationships.")


if __name__ == "__main__":
    main()