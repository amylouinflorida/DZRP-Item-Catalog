import sqlite3
from pathlib import Path

DB_PATH = Path("data/database/dayzrp_catalog.db")


def column_exists(cur, table, column):
    cur.execute(f"PRAGMA table_info({table})")
    return column in [row[1] for row in cur.fetchall()]


def add_column(cur, table, column, definition):
    if not column_exists(cur, table, column):
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        print(f"Added {table}.{column}")


conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Add needed item fields
add_column(cur, "items", "item_type", "TEXT")
add_column(cur, "items", "platform", "TEXT")
add_column(cur, "items", "weight", "INTEGER")
add_column(cur, "items", "size_x", "INTEGER")
add_column(cur, "items", "size_y", "INTEGER")
add_column(cur, "items", "spawn_status", "TEXT")

# Economy data from types.xml
cur.execute("""
CREATE TABLE IF NOT EXISTS spawn_data (
    item_id INTEGER PRIMARY KEY,
    nominal INTEGER,
    min INTEGER,
    lifetime INTEGER,
    restock INTEGER,
    quantmin INTEGER,
    quantmax INTEGER,
    deloot INTEGER,
    FOREIGN KEY (item_id) REFERENCES items(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS item_usages (
    item_id INTEGER,
    usage TEXT,
    UNIQUE(item_id, usage),
    FOREIGN KEY (item_id) REFERENCES items(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS item_tiers (
    item_id INTEGER,
    tier TEXT,
    UNIQUE(item_id, tier),
    FOREIGN KEY (item_id) REFERENCES items(id)
)
""")

# Compatibility / slot system
cur.execute("""
CREATE TABLE IF NOT EXISTS item_slots (
    item_id INTEGER,
    slot_name TEXT,
    direction TEXT CHECK(direction IN ('accepts', 'occupies')),
    UNIQUE(item_id, slot_name, direction),
    FOREIGN KEY (item_id) REFERENCES items(id)
)
""")

# Direct relationships
cur.execute("""
CREATE TABLE IF NOT EXISTS item_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_item_id INTEGER,
    target_item_id INTEGER,
    relationship_type TEXT,
    chance REAL,
    notes TEXT,
    UNIQUE(source_item_id, target_item_id, relationship_type),
    FOREIGN KEY (source_item_id) REFERENCES items(id),
    FOREIGN KEY (target_item_id) REFERENCES items(id)
)
""")

# EM / GM spawn approval policy
cur.execute("""
CREATE TABLE IF NOT EXISTS staff_spawn_policy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER UNIQUE,
    policy TEXT,
    role TEXT,
    notes TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(id)
)
""")

conn.commit()
conn.close()

print("Database migration complete.")