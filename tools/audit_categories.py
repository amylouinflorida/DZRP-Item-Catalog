import sqlite3
from pathlib import Path

DB_PATH = Path("data/database/dayzrp_catalog.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("\n=== CATEGORY AUDIT ===\n")

rows = cur.execute("""
    SELECT 
        COALESCE(category, 'NULL') AS category,
        COALESCE(subcategory, 'NULL') AS subcategory,
        COUNT(*) AS total
    FROM items
    GROUP BY category, subcategory
    ORDER BY category, subcategory
""").fetchall()

for row in rows:
    print(f"{row['category']:20} | {row['subcategory']:30} | {row['total']}")

conn.close()