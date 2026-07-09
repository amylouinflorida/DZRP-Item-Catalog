import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from database import get_connection

conn = get_connection()
cur = conn.cursor()

print("\n=== SLOT FILTERS ===")
rows = cur.execute("""
    SELECT slot_name, category, subcategory
    FROM slot_filters
    ORDER BY slot_name, sort_order
""").fetchall()

for row in rows:
    print(dict(row))

print("\n=== CURRENT ITEM CATEGORIES ===")
rows = cur.execute("""
    SELECT category, subcategory, COUNT(*) AS total
    FROM items
    GROUP BY category, subcategory
    ORDER BY category, subcategory
""").fetchall()

for row in rows:
    print(dict(row))

conn.close()