import sqlite3
from pathlib import Path

DB_PATH = Path("data/database/dayzrp_catalog.db")


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
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

    try:
        cursor.execute("ALTER TABLE favorites ADD COLUMN last_used TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
   
def add_mod(name, author=None, type=None, logo=None, website=None, description=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO mods (name, author, type, logo, website, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, author, type, logo, website, description))

    conn.commit()
    conn.close()


def add_item(classname, display_name, description=None, category=None, subcategory=None, mod_id=None, image=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO items (classname, display_name, description, category, subcategory, mod_id, image)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (classname, display_name, description, category, subcategory, mod_id, image))

    conn.commit()
    conn.close()


def get_all_items():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT items.*, mods.name AS mod_name
        FROM items
        LEFT JOIN mods ON items.mod_id = mods.id
        ORDER BY display_name
    """)

    items = cursor.fetchall()
    conn.close()

    return items


def get_item_by_classname(classname):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    search_term = f"%{query}%"

    cursor.execute("""
        SELECT items.*, mods.name AS mod_name
        FROM items
        LEFT JOIN mods ON items.mod_id = mods.id
        WHERE
            items.display_name LIKE ?
            OR items.classname LIKE ?
        ORDER BY items.display_name
    """, (
        search_term,
        search_term
    ))

    results = cursor.fetchall()
    conn.close()

    return results


def get_category_counts():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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


def get_mod_counts():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            mods.name,
            mods.logo,
            mods.author,
            mods.website,
            COUNT(items.id) AS item_count
        FROM mods
        LEFT JOIN items
            ON items.mod_id = mods.id
        GROUP BY mods.id
        ORDER BY mods.name
    """)

    mods = cursor.fetchall()
    conn.close()

    return mods


def get_dashboard_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM items")
    item_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM mods")
    mod_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tags")
    tag_count = cursor.fetchone()[0]

    relationship_count = 0

    conn.close()

    return {
        "items": item_count,
        "mods": mod_count,
        "tags": tag_count,
        "relationships": relationship_count
    }
def get_items_by_category(category):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
def get_items_by_mod(mod_name):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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

def get_items_by_mod(mod_name):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
def get_favorites():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT items.*, mods.name AS mod_name
        FROM favorites
        JOIN items ON favorites.item_id = items.id
        LEFT JOIN mods ON items.mod_id = mods.id
        ORDER BY CASE WHEN favorites.last_used IS NULL THEN 1 ELSE 0 END,
        favorites.last_used DESC,
        favorites.created_at DESC
    """)

    favorites = cursor.fetchall()
    conn.close()
    return favorites


def is_favorite(classname):
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM items WHERE classname = ?", (classname,))
    item = cursor.fetchone()

    if not item:
        conn.close()
        return

    item_id = item[0]

    cursor.execute("SELECT id FROM favorites WHERE item_id = ?", (item_id,))
    favorite = cursor.fetchone()

    if favorite:
        cursor.execute("DELETE FROM favorites WHERE item_id = ?", (item_id,))
    else:
        cursor.execute("INSERT INTO favorites (item_id) VALUES (?)", (item_id,))

    conn.commit()
    conn.close()

def get_notes_for_item(classname):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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

def delete_note(note_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM item_notes WHERE id = ?", (note_id,))

    conn.commit()
    conn.close()
def get_tags_for_item(classname):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
    conn = sqlite3.connect(DB_PATH)
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
        "SELECT id FROM tags WHERE name=?",
        (tag_name,)
    )
    tag_id = cursor.fetchone()[0]

    cursor.execute(
        "SELECT id FROM items WHERE classname=?",
        (classname,)
    )
    item_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT OR IGNORE INTO item_tags(item_id, tag_id)
        VALUES (?, ?)
    """, (item_id, tag_id))

    conn.commit()
    conn.close()
def get_tags_for_item(classname):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
    conn = sqlite3.connect(DB_PATH)
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
        "SELECT id FROM tags WHERE name=?",
        (tag_name,)
    )
    tag_id = cursor.fetchone()[0]

    cursor.execute(
        "SELECT id FROM items WHERE classname=?",
        (classname,)
    )
    item_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT OR IGNORE INTO item_tags(item_id, tag_id)
        VALUES (?, ?)
    """, (item_id, tag_id))

    conn.commit()
    conn.close()


def add_note_to_item(classname, note, author="Staff"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM items WHERE classname = ?", (classname,))
    item = cursor.fetchone()

    if item:
        cursor.execute("""
            INSERT INTO item_notes (item_id, author, note)
            VALUES (?, ?, ?)
        """, (item[0], author, note))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()

    add_mod(
        name="Vanilla DayZ",
        author="Bohemia Interactive",
        type="Vanilla",
        logo="vanilla.png",
        description="Base game DayZ items."
    )

    add_item(
        classname="Rag",
        display_name="Rag",
        description="A basic cloth item used for bandaging wounds and basic survival crafting.",
        category="Medical",
        subcategory="Bandage",
        mod_id=1,
        image="Rag.png"
    )
    add_item(
        classname="M4A1",
        display_name="M4A1",
        description="A modular assault rifle used for high-end military encounters.",
        category="Weapons",
        subcategory="Rifle",
        mod_id=1,
        image="M4A1.png"
    )

    add_item(
        classname="TacticalShirt_Black",
        display_name="Black Tactical Shirt",
        description="A durable tactical shirt with storage space and basic protection.",
        category="Clothing",
        subcategory="Shirt",
        mod_id=1,
        image="TacticalShirt_Black.png"
    )

    add_item(
        classname="BakedBeansCan",
        display_name="Baked Beans",
        description="A canned food item useful for basic survival.",
        category="Food",
        subcategory="Canned Food",
        mod_id=1,
        image="BakedBeansCan.png"
    )

    add_item(
        classname="Screwdriver",
        display_name="Screwdriver",
        description="A basic tool used for repairs, crafting, and utility tasks.",
        category="Tools",
        subcategory="Hand Tool",
        mod_id=1,
        image="Screwdriver.png"
    )

    add_item(
        classname="HuntingKnife",
        display_name="Hunting Knife",
        description="A survival knife used for skinning, cutting, and general wilderness tasks.",
        category="Survival",
        subcategory="Knife",
        mod_id=1,
        image="HuntingKnife.png"
    )



    print("✅ Starter data added successfully.")