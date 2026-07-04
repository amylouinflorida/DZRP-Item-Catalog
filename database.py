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
            OR items.description LIKE ?
            OR items.category LIKE ?
            OR items.subcategory LIKE ?
            OR mods.name LIKE ?
        ORDER BY items.display_name
    """, (
        search_term,
        search_term,
        search_term,
        search_term,
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
            COUNT(items.id) AS item_count
        FROM mods
        LEFT JOIN items ON items.mod_id = mods.id
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