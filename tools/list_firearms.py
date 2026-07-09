import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from database import get_connection

conn = get_connection()
cur = conn.cursor()

rows = cur.execute("""
    SELECT classname, display_name
    FROM items
    WHERE category = 'Weapons'
      AND subcategory = 'Firearms'
    ORDER BY display_name
""").fetchall()

for row in rows:
    print(f"{row['classname']} | {row['display_name']}")

conn.close()