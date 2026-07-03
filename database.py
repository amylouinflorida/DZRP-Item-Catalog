import sqlite3
from pathlib import Path

DB_PATH = Path("data/database/dayzrp_catalog.db")


def initialize_database():
    """Create the DayZRP Item Catalog database and required tables."""

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

    conn.commit()
    conn.close()

    print("✅ Database initialized successfully.")


def add_mod(name, author=None, type=None, logo=None, website=None, description=None):
    """Add a mod/source to the database if it does not already exist."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO mods (name, author, type, logo, website, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, author, type, logo, website, description))

    conn.commit()
    conn.close()


def add_item(classname, display_name, description=None, category=None, subcategory=None, mod_id=None, image=None):
    """Add an item to the database if it does not already exist."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO items (classname, display_name, description, category, subcategory, mod_id, image)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (classname, display_name, description, category, subcategory, mod_id, image))

    conn.commit()
    conn.close()


def get_all_items():
    """Return every item in the catalog."""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            items.*,
            mods.name AS mod_name
        FROM items
        LEFT JOIN mods
            ON items.mod_id = mods.id
        ORDER BY display_name
    """)

    items = cursor.fetchall()
    conn.close()

    return items


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

    print("✅ Starter data added successfully.")