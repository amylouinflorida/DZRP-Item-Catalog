import sqlite3
from pathlib import Path

DB_PATH = Path("data/database/dayzrp_catalog.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
    UPDATE items
    SET category = 'Weapons',
        subcategory = 'Melee',
        item_type = 'Melee Weapon'
    WHERE category = 'Survival'
       OR classname LIKE '%Knife%'
       OR display_name LIKE '%Knife%'
""")

conn.commit()
print("Updated rows:", cur.rowcount)

conn.close()