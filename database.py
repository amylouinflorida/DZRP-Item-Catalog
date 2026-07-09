import sqlite3
from pathlib import Path

from catalog.taxonomy import classify_item

DB_PATH = Path("data/database/dayzrp_catalog.db")


# ============================================================
# Connection
# ============================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# Database Initialization
# ============================================================

def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            author TEXT,
            type TEXT,
            logo TEXT,
            website TEXT,
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            classname TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            subcategory TEXT,
            mod_id INTEGER,
            image TEXT,
            FOREIGN KEY (mod_id) REFERENCES mods(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS item_tags (
            item_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (item_id, tag_id),
            FOREIGN KEY (item_id) REFERENCES items(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER UNIQUE NOT NULL,
            use_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_used TEXT,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS item_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            author TEXT DEFAULT 'Staff',
            note TEXT NOT NULL,
            helpful_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS item_flags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            issue_type TEXT NOT NULL,
            note TEXT,
            status TEXT DEFAULT 'open',
            created_by TEXT DEFAULT 'Staff',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            resolved_at TEXT,
            suggested_category TEXT,
            suggested_subcategory TEXT,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS item_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_item_id INTEGER,
            target_item_id INTEGER,
            relationship_type TEXT,
            chance REAL,
            notes TEXT,
            UNIQUE (source_item_id, target_item_id, relationship_type),
            FOREIGN KEY (source_item_id) REFERENCES items(id),
            FOREIGN KEY (target_item_id) REFERENCES items(id)
        )
    """)

    initialize_preset_tables(cursor)
    initialize_slot_filter_table(cursor)

    run_safe_migrations(cursor)

    conn.commit()
    conn.close()


def run_safe_migrations(cursor):
    migrations = [
        ("favorites", "last_used", "TEXT"),
        ("item_flags", "suggested_category", "TEXT"),
        ("item_flags", "suggested_subcategory", "TEXT"),
    ]

    for table, column, column_type in migrations:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
        except sqlite3.OperationalError:
            pass


# ============================================================
# Preset Tables
# ============================================================

def initialize_preset_tables(cursor=None):
    close_connection = False

    if cursor is None:
        conn = get_connection()
        cursor = conn.cursor()
        close_connection = True

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS presets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            preset_type TEXT NOT NULL DEFAULT 'personal',
            created_by TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preset_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            preset_id INTEGER NOT NULL,
            slot_name TEXT NOT NULL,
            item_id INTEGER,
            quantity INTEGER NOT NULL DEFAULT 1,
            notes TEXT,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY (preset_id) REFERENCES presets(id),
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS slot_definitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_name TEXT UNIQUE NOT NULL,
            slot_group TEXT NOT NULL,
            sort_order INTEGER DEFAULT 0
        )
    """)

    if close_connection:
        conn.commit()
        conn.close()


def seed_slot_definitions():
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM slot_definitions")

    slots = [
        ("Head", "Character", 10),
        ("Face", "Character", 20),
        ("Torso", "Character", 30),
        ("Chest / Vest", "Character", 40),
        ("Hands", "Character", 50),
        ("Legs", "Character", 60),
        ("Feet", "Character", 70),
        ("Backpack", "Character", 80),

        ("Primary Weapon 1", "Weapons", 100),
        ("Primary Weapon 2", "Weapons", 110),
        ("Handgun", "Weapons", 120),
        ("Melee", "Weapons", 130),

        ("Medical", "Supplies", 200),
        ("Tools", "Supplies", 210),
        ("Communications", "Supplies", 220),
        ("Navigation", "Supplies", 230),
        ("Food / Drink", "Supplies", 240),
        ("Miscellaneous", "Supplies", 250),
    ]

    cursor.executemany("""
        INSERT INTO slot_definitions (slot_name, slot_group, sort_order)
        VALUES (?, ?, ?)
    """, slots)

    conn.commit()
    conn.close()
    


# ============================================================
# Slot Filters
# ============================================================

def initialize_slot_filter_table(cursor=None):
    close_connection = False

    if cursor is None:
        conn = get_connection()
        cursor = conn.cursor()
        close_connection = True

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS slot_filters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_name TEXT NOT NULL,
            category TEXT,
            subcategory TEXT,
            sort_order INTEGER DEFAULT 0
        )
    """)

    if close_connection:
        conn.commit()
        conn.close()


def seed_slot_filters():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM slot_filters")

    filters = [
        ("Head", "Clothing", "Headwear", 10),
        ("Face", "Clothing", "Facewear", 20),
        ("Torso", "Clothing", "Shirts", 30),
        ("Torso", "Clothing", "Jackets", 31),
        ("Chest / Vest", "Clothing", "Vests", 40),
        ("Hands", "Clothing", "Gloves", 50),
        ("Legs", "Clothing", "Pants", 60),
        ("Feet", "Clothing", "Footwear", 70),
        ("Backpack", "Clothing", "Backpacks", 80),

        ("Primary Weapon 1", "Weapons", "Assault Rifles", 100),
        ("Primary Weapon 1", "Weapons", "Battle Rifles", 101),
        ("Primary Weapon 1", "Weapons", "Bolt-Action Rifles", 102),
        ("Primary Weapon 1", "Weapons", "Designated Marksman Rifles", 103),
        ("Primary Weapon 1", "Weapons", "Sniper Rifles", 104),
        ("Primary Weapon 1", "Weapons", "Submachine Guns", 105),
        ("Primary Weapon 1", "Weapons", "Shotguns", 106),
        ("Primary Weapon 1", "Weapons", "Machine Guns", 107),

        ("Primary Weapon 2", "Weapons", "Assault Rifles", 110),
        ("Primary Weapon 2", "Weapons", "Battle Rifles", 111),
        ("Primary Weapon 2", "Weapons", "Bolt-Action Rifles", 112),
        ("Primary Weapon 2", "Weapons", "Designated Marksman Rifles", 113),
        ("Primary Weapon 2", "Weapons", "Sniper Rifles", 114),
        ("Primary Weapon 2", "Weapons", "Submachine Guns", 115),
        ("Primary Weapon 2", "Weapons", "Shotguns", 116),
        ("Primary Weapon 2", "Weapons", "Machine Guns", 117),

        ("Handgun", "Weapons", "Pistols", 120),
        ("Handgun", "Weapons", "Revolvers", 121),
        ("Melee", "Weapons", "Melee", 130),

        ("Medical", "Medical", None, 200),
        ("Tools", "Tools", None, 210),
        ("Communications", "Electronics", "Radios", 220),
        ("Navigation", "Electronics", "GPS", 230),
        ("Food / Drink", "Food", None, 240),
        ("Miscellaneous", "Miscellaneous", None, 250),
    ]

    cursor.executemany("""
        INSERT INTO slot_filters (slot_name, category, subcategory, sort_order)
        VALUES (?, ?, ?, ?)
    """, filters)

    conn.commit()
    conn.close()


def get_slot_filters(slot_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT slot_name, category, subcategory
        FROM slot_filters
        WHERE slot_name = ?
        ORDER BY sort_order
    """, (slot_name,))

    filters = cursor.fetchall()
    conn.close()
    return filters


# ============================================================
# Mods
# ============================================================

def add_mod(name, author=None, type=None, logo=None, website=None, description=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO mods (name, author, type, logo, website, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, author, type, logo, website, description))

    conn.commit()
    conn.close()


def get_or_create_mod(name, author=None, type=None, logo=None, website=None, description=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO mods (name, author, type, logo, website, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, author, type, logo, website, description))

    cursor.execute("SELECT id FROM mods WHERE name = ?", (name,))
    mod = cursor.fetchone()

    conn.commit()
    conn.close()

    return mod["id"]


def get_mod_counts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            mods.name,
            mods.logo,
            mods.author,
            mods.website,
            COUNT(items.id) AS item_count
        FROM mods
        LEFT JOIN items ON items.mod_id = mods.id
        GROUP BY mods.id
        ORDER BY mods.name
    """)

    mods = cursor.fetchall()
    conn.close()
    return mods


def get_items_by_mod(mod_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT items.*, mods.name AS mod_name
        FROM items
        LEFT JOIN mods ON items.mod_id = mods.id
        WHERE mods.name = ?
        ORDER BY items.display_name
    """, (mod_name,))

    items = cursor.fetchall()
    conn.close()
    return items


# ============================================================
# Items
# ============================================================

def add_item(classname, display_name, description=None, category=None, subcategory=None, mod_id=None, image=None):
    conn = get_connection()
    cursor = conn.cursor()

    mod_name = ""

    if mod_id:
        cursor.execute("SELECT name FROM mods WHERE id = ?", (mod_id,))
        mod = cursor.fetchone()
        if mod:
            mod_name = mod["name"]

    if not category or not subcategory:
        category, subcategory = classify_item(classname, display_name, mod_name)

    cursor.execute("""
        INSERT OR IGNORE INTO items (
            classname,
            display_name,
            description,
            category,
            subcategory,
            mod_id,
            image
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        classname,
        display_name,
        description,
        category,
        subcategory,
        mod_id,
        image,
    ))

    conn.commit()
    conn.close()


def get_all_items():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT items.*, mods.name AS mod_name
        FROM items
        LEFT JOIN mods ON items.mod_id = mods.id
        ORDER BY items.display_name
    """)

    items = cursor.fetchall()
    conn.close()
    return items


def get_item_by_id(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, classname, display_name, category, subcategory
        FROM items
        WHERE id = ?
    """, (item_id,))

    item = cursor.fetchone()
    conn.close()
    return item


def get_item_by_classname(classname):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            items.*,
            mods.name AS mod_name,
            mods.author AS mod_author,
            mods.type AS mod_type,
            mods.logo AS mod_logo
        FROM items
        LEFT JOIN mods ON items.mod_id = mods.id
        WHERE items.classname = ?
    """, (classname,))

    item = cursor.fetchone()
    conn.close()
    return item


def search_items(query):
    conn = get_connection()
    cursor = conn.cursor()

    search_term = f"%{query}%"

    cursor.execute("""
        SELECT items.*, mods.name AS mod_name
        FROM items
        LEFT JOIN mods ON items.mod_id = mods.id
        WHERE items.display_name LIKE ?
           OR items.classname LIKE ?
        ORDER BY items.display_name
    """, (search_term, search_term))

    results = cursor.fetchall()
    conn.close()
    return results


def find_items_for_recategory(search_term):
    conn = get_connection()
    cursor = conn.cursor()

    like = f"%{search_term}%"

    cursor.execute("""
        SELECT id, classname, display_name, category, subcategory
        FROM items
        WHERE classname LIKE ?
           OR display_name LIKE ?
        ORDER BY display_name
        LIMIT 50
    """, (like, like))

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_items_by_category(category):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT items.*, mods.name AS mod_name
        FROM items
        LEFT JOIN mods ON items.mod_id = mods.id
        WHERE COALESCE(NULLIF(items.category, ''), 'Uncategorized') = ?
        ORDER BY items.display_name
    """, (category,))

    items = cursor.fetchall()
    conn.close()
    return items


def update_item_category(item_id, category, subcategory):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE items
        SET category = ?,
            subcategory = ?
        WHERE id = ?
    """, (category, subcategory, item_id))

    conn.commit()
    conn.close()


def reclassify_mod_items(mod_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT items.id, items.classname, items.display_name
        FROM items
        JOIN mods ON items.mod_id = mods.id
        WHERE mods.name = ?
    """, (mod_name,))

    items = cursor.fetchall()
    updated = 0

    for item in items:
        category, subcategory = classify_item(
            item["classname"],
            item["display_name"],
            mod_name,
        )

        cursor.execute("""
            UPDATE items
            SET category = ?, subcategory = ?
            WHERE id = ?
        """, (category, subcategory, item["id"]))

        updated += 1

    conn.commit()
    conn.close()

    print(f"✅ Reclassified {updated} items from {mod_name}.")


# ============================================================
# Categories / Dashboard Cards
# ============================================================

MAIN_CATEGORIES = {
    "Weapons": {"image": "weapons.png"},
    "Clothing": {"image": "clothing.png"},
    "Medical": {"image": "medical.png"},
    "Food": {"image": "food.png"},
    "Tools": {"image": "tools.png"},
    "Vehicles": {"image": "vehicles.png"},
    "Base Building": {"image": "base_building.png"},
    "Electronics": {"image": "electronics.png"},
    "Miscellaneous": {"image": "miscellaneous.png"},
}


def get_category_counts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COALESCE(NULLIF(category, ''), 'Uncategorized') AS category,
            COUNT(*) AS item_count
        FROM items
        GROUP BY COALESCE(NULLIF(category, ''), 'Uncategorized')
        ORDER BY category
    """)

    categories = cursor.fetchall()
    conn.close()
    return categories


def get_main_category_cards():
    conn = get_connection()
    cursor = conn.cursor()

    cards = []

    for category_name, data in MAIN_CATEGORIES.items():
        row = cursor.execute("""
            SELECT COUNT(*) AS item_count
            FROM items
            WHERE category = ?
        """, (category_name,)).fetchone()

        cards.append({
            "name": category_name,
            "image": data["image"],
            "item_count": row["item_count"],
        })

    conn.close()
    return cards


# ============================================================
# Relationships
# ============================================================

def get_relationships_for_item(classname):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            target.classname,
            target.display_name,
            target.category,
            target.subcategory,
            target.image,
            r.relationship_type,
            r.chance,
            r.notes
        FROM item_relationships r
        JOIN items source ON source.id = r.source_item_id
        JOIN items target ON target.id = r.target_item_id
        WHERE source.classname = ?
        ORDER BY target.display_name
    """, (classname,))

    spawns_with = cursor.fetchall()

    cursor.execute("""
        SELECT
            source.classname,
            source.display_name,
            source.category,
            source.subcategory,
            source.image,
            r.relationship_type,
            r.chance,
            r.notes
        FROM item_relationships r
        JOIN items source ON source.id = r.source_item_id
        JOIN items target ON target.id = r.target_item_id
        WHERE target.classname = ?
        ORDER BY source.display_name
    """, (classname,))

    spawned_in = cursor.fetchall()
    conn.close()

    return {
        "spawns_with": spawns_with,
        "spawned_in": spawned_in,
    }


# ============================================================
# Favorites / Pins
# ============================================================

def get_favorites():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT items.*, mods.name AS mod_name
        FROM favorites
        JOIN items ON favorites.item_id = items.id
        LEFT JOIN mods ON items.mod_id = mods.id
        ORDER BY
            CASE WHEN favorites.last_used IS NULL THEN 1 ELSE 0 END,
            favorites.last_used DESC,
            favorites.created_at DESC
    """)

    favorites = cursor.fetchall()
    conn.close()
    return favorites


def is_favorite(classname):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT favorites.id
        FROM favorites
        JOIN items ON favorites.item_id = items.id
        WHERE items.classname = ?
    """, (classname,))

    result = cursor.fetchone()
    conn.close()
    return result is not None


def mark_favorite_used(classname):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE favorites
        SET last_used = CURRENT_TIMESTAMP
        WHERE item_id = (
            SELECT id FROM items WHERE classname = ?
        )
    """, (classname,))

    conn.commit()
    conn.close()


def toggle_favorite(classname):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM items WHERE classname = ?", (classname,))
    item = cursor.fetchone()

    if not item:
        conn.close()
        return

    item_id = item["id"]

    cursor.execute("SELECT id FROM favorites WHERE item_id = ?", (item_id,))
    favorite = cursor.fetchone()

    if favorite:
        cursor.execute("DELETE FROM favorites WHERE item_id = ?", (item_id,))
    else:
        cursor.execute("INSERT INTO favorites (item_id) VALUES (?)", (item_id,))

    conn.commit()
    conn.close()


# ============================================================
# Staff Notes
# ============================================================

def get_notes_for_item(classname):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT item_notes.*
        FROM item_notes
        JOIN items ON item_notes.item_id = items.id
        WHERE items.classname = ?
        ORDER BY item_notes.helpful_count DESC, item_notes.created_at DESC
    """, (classname,))

    notes = cursor.fetchall()
    conn.close()
    return notes


def add_note_to_item(classname, note, author="Staff"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM items WHERE classname = ?", (classname,))
    item = cursor.fetchone()

    if item:
        cursor.execute("""
            INSERT INTO item_notes (item_id, author, note)
            VALUES (?, ?, ?)
        """, (item["id"], author, note))

    conn.commit()
    conn.close()


def delete_note(note_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM item_notes WHERE id = ?", (note_id,))

    conn.commit()
    conn.close()


# ============================================================
# Tags
# ============================================================

def get_tags_for_item(classname):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tags.*
        FROM tags
        JOIN item_tags ON tags.id = item_tags.tag_id
        JOIN items ON items.id = item_tags.item_id
        WHERE items.classname = ?
        ORDER BY tags.name
    """, (classname,))

    tags = cursor.fetchall()
    conn.close()
    return tags


def add_tag_to_item(classname, tag_name):
    conn = get_connection()
    cursor = conn.cursor()

    tag_name = tag_name.strip().lower()

    if not tag_name:
        conn.close()
        return

    cursor.execute("INSERT OR IGNORE INTO tags(name) VALUES (?)", (tag_name,))
    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
    tag = cursor.fetchone()

    cursor.execute("SELECT id FROM items WHERE classname = ?", (classname,))
    item = cursor.fetchone()

    if tag and item:
        cursor.execute("""
            INSERT OR IGNORE INTO item_tags(item_id, tag_id)
            VALUES (?, ?)
        """, (item["id"], tag["id"]))

    conn.commit()
    conn.close()


# ============================================================
# Flags / Reports
# ============================================================

def add_item_flag(classname, issue_type, note=None, created_by="Staff", suggested_category=None, suggested_subcategory=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM items WHERE classname = ?", (classname,))
    item = cursor.fetchone()

    if not item:
        conn.close()
        return False

    cursor.execute("""
        INSERT INTO item_flags (
            item_id,
            issue_type,
            note,
            created_by,
            suggested_category,
            suggested_subcategory
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        item["id"],
        issue_type,
        note,
        created_by,
        suggested_category,
        suggested_subcategory,
    ))

    conn.commit()
    conn.close()
    return True


def get_open_item_flags():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            item_flags.*,
            items.classname,
            items.display_name,
            items.category,
            items.subcategory,
            mods.name AS mod_name
        FROM item_flags
        JOIN items ON item_flags.item_id = items.id
        LEFT JOIN mods ON items.mod_id = mods.id
        WHERE item_flags.status = 'open'
        ORDER BY item_flags.created_at DESC
    """)

    flags = cursor.fetchall()
    conn.close()
    return flags


def resolve_item_flag(flag_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE item_flags
        SET status = 'resolved',
            resolved_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (flag_id,))

    conn.commit()
    conn.close()


# ============================================================
# Dashboard / Management
# ============================================================

def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM items")
    item_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM mods")
    mod_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM tags")
    tag_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM item_relationships")
    relationship_count = cursor.fetchone()["count"]

    conn.close()

    return {
        "items": item_count,
        "mods": mod_count,
        "tags": tag_count,
        "relationships": relationship_count,
    }


def get_management_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM items")
    total_items = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM mods")
    total_mods = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM item_relationships")
    total_relationships = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM item_flags
        WHERE status = 'open'
    """)
    open_flags = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM items
        WHERE category = 'Miscellaneous'
           OR category IS NULL
           OR category = ''
    """)
    miscellaneous_items = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM items
        WHERE image IS NULL
           OR image = ''
    """)
    missing_images = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM items
        WHERE description IS NULL
           OR description = ''
    """)
    missing_descriptions = cursor.fetchone()["count"]

    conn.close()

    return {
        "total_items": total_items,
        "total_mods": total_mods,
        "total_relationships": total_relationships,
        "open_flags": open_flags,
        "miscellaneous_items": miscellaneous_items,
        "missing_images": missing_images,
        "missing_descriptions": missing_descriptions,
    }


# ============================================================
# Presets
# ============================================================

def get_presets_by_type(preset_type="personal"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, description, preset_type, created_at, updated_at
        FROM presets
        WHERE preset_type = ?
        ORDER BY name
    """, (preset_type,))

    presets = cursor.fetchall()
    conn.close()
    return presets


def create_preset(name, description="", preset_type="personal"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO presets (name, description, preset_type)
        VALUES (?, ?, ?)
    """, (name, description, preset_type))

    conn.commit()
    preset_id = cursor.lastrowid
    conn.close()
    return preset_id


def get_preset_by_id(preset_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, description, preset_type, created_at, updated_at
        FROM presets
        WHERE id = ?
    """, (preset_id,))

    preset = cursor.fetchone()
    conn.close()
    return preset


def get_slot_definitions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, slot_name, slot_group, sort_order
        FROM slot_definitions
        ORDER BY slot_group, sort_order
    """)

    slots = cursor.fetchall()
    conn.close()
    return slots


def get_preset_items(preset_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            preset_items.slot_name,
            items.id,
            items.display_name,
            items.classname,
            items.image
        FROM preset_items
        JOIN items ON preset_items.item_id = items.id
        WHERE preset_items.preset_id = ?
    """, (preset_id,))

    rows = cursor.fetchall()
    conn.close()

    return {row["slot_name"]: row for row in rows}


def set_preset_slot_item(preset_id, slot_name, item_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM preset_items
        WHERE preset_id = ?
          AND slot_name = ?
    """, (preset_id, slot_name))

    cursor.execute("""
        INSERT INTO preset_items
            (preset_id, slot_name, item_id)
        VALUES (?, ?, ?)
    """, (preset_id, slot_name, item_id))

    conn.commit()
    conn.close()


def get_items_for_slot(slot_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, subcategory
        FROM slot_filters
        WHERE slot_name = ?
        ORDER BY sort_order
    """, (slot_name,))

    filters = cursor.fetchall()

    print("SLOT CLICKED:", slot_name)
    print("FILTERS FOUND:", [dict(row) for row in filters])

    if not filters:
        conn.close()
        return []

    clauses = []
    values = []

    for item_filter in filters:
        if item_filter["subcategory"]:
            clauses.append("(category = ? AND subcategory = ?)")
            values.extend([item_filter["category"], item_filter["subcategory"]])
        else:
            clauses.append("(category = ?)")
            values.append(item_filter["category"])

    sql = f"""
        SELECT id, display_name, classname, image, category, subcategory
        FROM items
        WHERE {" OR ".join(clauses)}
        ORDER BY display_name
    """

    print("SQL:", sql)
    print("VALUES:", values)

    cursor.execute(sql, values)
    items = cursor.fetchall()

    print("ITEMS FOUND:", len(items))

    conn.close()
    return items

# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    initialize_database()
    seed_slot_definitions()
    seed_slot_filters()
    print("✅ Database initialized successfully.")