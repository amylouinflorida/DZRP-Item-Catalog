import sqlite3
from pathlib import Path

DB_PATH = Path("data/database/dayzrp_catalog.db")

print("Database exists:", DB_PATH.exists())
print("Location:", DB_PATH.resolve())

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("\nItems:\n")

cur.execute("""
SELECT
    id,
    classname,
    display_name,
    item_type,
    platform
FROM items
LIMIT 20
""")

rows = cur.fetchall()

for row in rows:
    print(row)

conn.close()