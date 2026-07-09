import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "data" / "database" / "dayzrp_catalog.db"


def ensure_relationship_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS item_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_item_id INTEGER NOT NULL,
            target_item_id INTEGER NOT NULL,
            relationship_type TEXT NOT NULL,
            chance REAL,
            notes TEXT
        )
    """)


def clear_old_compatibility_relationships(cursor):
    cursor.execute("""
        DELETE FROM item_relationships
        WHERE relationship_type = 'compatible_attachment'
    """)


def build_relationships(cursor):
    accepted_slots = cursor.execute("""
        SELECT 
            items.id,
            items.classname,
            items.display_name,
            item_slots.slot_name
        FROM item_slots
        JOIN items ON items.id = item_slots.item_id
        WHERE item_slots.direction = 'accepts'
    """).fetchall()

    created = 0

    for weapon_id, weapon_classname, weapon_name, slot_name in accepted_slots:
        compatible_items = cursor.execute("""
            SELECT 
                items.id,
                items.classname,
                items.display_name
            FROM item_slots
            JOIN items ON items.id = item_slots.item_id
            WHERE item_slots.direction = 'uses'
              AND item_slots.slot_name = ?
              AND items.id != ?
        """, (slot_name, weapon_id)).fetchall()

        if compatible_items:
            print(f"\n{weapon_name or weapon_classname}")
            print(f"  Slot: {slot_name}")

        for target_id, target_classname, target_name in compatible_items:
            print(f"    -> {target_name or target_classname}")

            cursor.execute("""
    INSERT OR IGNORE INTO item_relationships (
        source_item_id,
        target_item_id,
        relationship_type,
        notes
    )
    VALUES (?, ?, ?, ?)
""", (
    weapon_id,
    target_id,
    "compatible_attachment",
    f"slot:{slot_name}"
))

            created += 1

    return created


def main():
    print("=" * 80)
    print("AJW Relationship Builder Starting")
    print("=" * 80)

    print("Database:", DB_PATH)
    print("DB exists:", DB_PATH.exists())

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    ensure_relationship_table(cursor)
    clear_old_compatibility_relationships(cursor)

    created = build_relationships(cursor)

    conn.commit()

    total = cursor.execute("""
        SELECT COUNT(*)
        FROM item_relationships
        WHERE relationship_type = 'compatible_attachment'
    """).fetchone()[0]

    conn.close()

    print("\n" + "=" * 80)
    print("RELATIONSHIP BUILD COMPLETE")
    print("=" * 80)
    print("Relationships created this run:", created)
    print("Total compatible_attachment relationships:", total)


if __name__ == "__main__":
    main()