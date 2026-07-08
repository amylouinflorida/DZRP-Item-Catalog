import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "data" / "database" / "dayzrp_catalog.db"

print("Using database:", DB_PATH.resolve())

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
    UPDATE mods
    SET logo = ?
    WHERE name = ?
""", ("ams.png", "Additional Medical Supplies"))

conn.commit()

print("Rows updated:", cur.rowcount)

conn.close()