MOD_NAME = "AJW Weapons"

def get_or_create_mod(conn):
    cur = conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO mods (name, author, type, logo, website, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        MOD_NAME,
        "AJ45",
        "Weapons",
        "mods/ajw-weapons.png",
        "https://steamcommunity.com/sharedfiles/filedetails/?id=3571685323",
        "AJW Weapons item import."
    ))

    cur.execute("SELECT id FROM mods WHERE name = ?", (MOD_NAME,))
    return cur.fetchone()[0]