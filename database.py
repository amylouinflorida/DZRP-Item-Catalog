import sqlite3
from pathlib import Path

# Path to our SQLite database
DB_PATH = Path("data/database/dayzrp_catalog.db")


def initialize_database():
    """Create the DayZRP Item Catalog database and required tables."""

    # Make sure the database folder exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Connect to SQLite (creates the database if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the Items table
    # Create the Mods table
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

# Create the Items table
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

    # Save changes
    conn.commit()

    # Close the database
    conn.close()

    print("✅ Database initialized successfully.")


if __name__ == "__main__":
    initialize_database()