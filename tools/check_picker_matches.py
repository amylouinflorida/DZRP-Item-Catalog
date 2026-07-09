import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from database import get_connection

conn = get_connection()
cur = conn.cursor()

print("\n=== SLOT FILTERS ===")
filters = cur.execute("""
    SELECT slot_name, category, subcategory
    FROM slot_filters
    ORDER BY slot_name, sort_order
""").fetchall()

for row in filters:
    print(dict(row))

print("\n=== ITEM CATEGORY/SUBCATEGORY COUNTS ===")
counts = cur.execute("""
    SELECT category, subcategory, COUNT(*) AS total
    FROM items
    GROUP BY category, subcategory
    ORDER BY category, subcategory
""").fetchall()

for row in counts:
    print(dict(row))

print("\n=== MATCH TEST ===")
for row in filters:
    if row["subcategory"]:
        total = cur.execute("""
            SELECT COUNT(*) AS total
            FROM items
            WHERE category = ?
              AND subcategory = ?
        """, (row["category"], row["subcategory"])).fetchone()["total"]
    else:
        total = cur.execute("""
            SELECT COUNT(*) AS total
            FROM items
            WHERE category = ?
        """, (row["category"],)).fetchone()["total"]

    print(f"{row['slot_name']}: {row['category']} / {row['subcategory']} -> {total}")

conn.close()