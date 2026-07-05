# scripts/update_schema.py
import sqlite3
from pathlib import Path

DB_PATH = Path("data/database/dayzrp_catalog.db")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

def add_column(table, column, definition):
    cur.execute(f"PRAGMA table_info({table})")
    existing = [row[1] for row in cur.fetchall()]
    if column not in existing:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        print(f"Added {table}.{column}")

add_column("items", "item_type", "TEXT")
add_column("items", "platform", "TEXT")
add_column("items", "weight", "INTEGER")
add_column("items", "size_x", "INTEGER")
add_column("items", "size_y", "INTEGER")

conn.commit()
conn.close()

print("Schema update complete.")