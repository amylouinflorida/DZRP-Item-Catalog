import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

print("Starting preset setup...")
print("Root dir:", ROOT_DIR)

try:
    from database import initialize_preset_tables, seed_slot_definitions
    print("Imported preset setup functions successfully.")
except Exception as e:
    print("IMPORT ERROR:", e)
    raise

try:
    initialize_preset_tables()
    print("Preset tables created.")

    seed_slot_definitions()
    print("Slot definitions seeded.")

except Exception as e:
    print("SETUP ERROR:", e)
    raise

print("DONE: Preset tables created and slot definitions seeded.")