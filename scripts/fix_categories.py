import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from database import DB_PATH, update_item_category, debug_item

print("Using database:", DB_PATH.resolve())

before = debug_item("AMS_Heatpack")
print("Before:", dict(before) if before else "NOT FOUND")

update_item_category("AMS_Heatpack", "Equipment", "Survival")

after = debug_item("AMS_Heatpack")

update_item_category("AJW_TLRLight", "Attachments", "Flashlights")

print("After:", dict(after) if after else "NOT FOUND")