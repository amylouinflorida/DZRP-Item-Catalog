import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from database import get_connection

conn = get_connection()
cur = conn.cursor()

rows = cur.execute("""
    SELECT category, subcategory, COUNT(*) AS total
    FROM items
    GROUP BY category, subcategory
    ORDER BY category, subcategory
""").fetchall()

print("\nREAL CATEGORIES IN DATABASE:\n")

for row in rows:
    print(f"{row['category']} / {row['subcategory']} = {row['total']}")

conn.close()