import sqlite3
from pathlib import Path

DB_PATH = Path("data/database/dayzrp_catalog.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
    UPDATE items
    SET category = 'Weapons'
    WHERE category = 'Attachments'
""")

conn.commit()
print("Rows updated:", cur.rowcount)

conn.close()