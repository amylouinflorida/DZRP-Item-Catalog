import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from database import initialize_slot_filter_table, seed_slot_filters

initialize_slot_filter_table()
seed_slot_filters()

print("Slot filters created and seeded.")