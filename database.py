import sqlite3
from pathlib import Path

from catalog.taxonomy import classify_item

DB_PATH = Path("data/database/dayzrp_catalog.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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
            UNIQUE (
                source_item_id,
                target_item_id,
                relationship_type
            ),
            FOREIGN KEY (source_item_id) REFERENCES items(id),
            FOREIGN KEY (target_item_id) REFERENCES items(id)
        )
    """)

    # Safe migrations for older databases.
    for table, column, column_type in [
        ("favorites", "last_used", "TEXT"),
        ("item_flags", "suggested_category", "TEXT"),
        ("item_flags", "suggested_subcategory", "TEXT"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()


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
        image
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
            mod_name
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
        "spawned_in": spawned_in
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

    cursor.execute(
        "INSERT OR IGNORE INTO tags(name) VALUES (?)",
        (tag_name,)
    )

    cursor.execute(
        "SELECT id FROM tags WHERE name = ?",
        (tag_name,)
    )
    tag = cursor.fetchone()

    cursor.execute(
        "SELECT id FROM items WHERE classname = ?",
        (classname,)
    )
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
        suggested_subcategory
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
# Dashboard
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
        "relationships": relationship_count
    }
# ============================================================
# Management
# ============================================================
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

if __name__ == "__main__":
    initialize_database()
    print("✅ Database initialized successfully.")