import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from database import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("DELETE FROM slot_definitions")

slots = [
    ("Head", "Character", 10),
    ("Face", "Character", 20),
    ("Torso", "Character", 30),
    ("Chest / Vest", "Character", 40),
    ("Hands", "Character", 50),
    ("Legs", "Character", 60),
    ("Feet", "Character", 70),
    ("Backpack", "Character", 80),

    ("Primary Weapon 1", "Weapons", 100),
    ("Primary Weapon 2", "Weapons", 110),
    ("Handgun", "Weapons", 120),
    ("Melee", "Weapons", 130),

    ("Medical", "Supplies", 200),
    ("Tools", "Supplies", 210),
    ("Communications", "Supplies", 220),
    ("Navigation", "Supplies", 230),
    ("Food / Drink", "Supplies", 240),
    ("Miscellaneous", "Supplies", 250),
]

cur.executemany("""
    INSERT INTO slot_definitions
        (slot_name, slot_group, sort_order)
    VALUES (?, ?, ?)
""", slots)

conn.commit()
conn.close()

print("Preset slot definitions reset to parent slots only.")