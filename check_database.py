import sqlite3
from pathlib import Path

DB_PATH = Path("data/database/dayzrp_catalog.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

queries = {
    "Total Items": "SELECT COUNT(*) AS count FROM items",
    "Items by Category": """
        SELECT COALESCE(NULLIF(category, ''), 'Uncategorized') AS label, COUNT(*) AS count
        FROM items
        GROUP BY label
        ORDER BY count DESC
    """,
    "Do Not Spawn": """
        SELECT COUNT(*) AS count
        FROM spawn_data
        WHERE nominal = 0
    """,
    "Active Economy": """
        SELECT COUNT(*) AS count
        FROM spawn_data
        WHERE nominal > 0
    """,
    "Items Missing Category": """
        SELECT COUNT(*) AS count
        FROM items
        WHERE category IS NULL OR category = ''
    """,
    "Items by Mod": """
        SELECT COALESCE(mods.name, 'Unknown') AS label, COUNT(items.id) AS count
        FROM items
        LEFT JOIN mods ON items.mod_id = mods.id
        GROUP BY label
        ORDER BY count DESC
    """
}

for title, sql in queries.items():
    print(f"\n{title}")
    print("-" * len(title))

    cur.execute(sql)
    rows = cur.fetchall()

    for row in rows:
        if "label" in row.keys():
            print(f"{row['label']}: {row['count']}")
        else:
            print(row["count"])

conn.close()