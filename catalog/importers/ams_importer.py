import sqlite3
import xml.etree.ElementTree as ET

from database import add_item

MOD_NAME = "Additional Medical Supplies"
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter

ROOT_DIR = Path(__file__).resolve().parents[1]

sys.path.append(str(ROOT_DIR))

from database import initialize_database, get_or_create_mod, add_item
from taxonomy import classify_item


TYPES_PATH = ROOT_DIR / "data" / "imports" / "ams" / "types" / "ams_types.xml"

MOD_NAME = "Additional Medical Supplies"


def import_ams():
    initialize_database()

    mod_id = get_or_create_mod(
        name=MOD_NAME,
        author="Unknown",
        type="Medical Mod",
        logo=None,
        description="Additional Medical Supplies mod items."
    )

    tree = ET.parse(TYPES_PATH)
    root = tree.getroot()

    summary = Counter()
    imported = 0

    for type_node in root.findall("type"):
        classname = type_node.attrib.get("name")

        if not classname or not classname.startswith("AMS_"):
            continue

        category, subcategory = classify_item(
            classname=classname,
            display_name=classname,
            mod_name=MOD_NAME
        )

        add_item(
            classname=classname,
            display_name=classname,
            description=None,
            category=category,
            subcategory=subcategory,
            mod_id=mod_id,
            image=None
        )

        summary[f"{category} > {subcategory}"] += 1
        imported += 1

    print(f"✅ Imported {imported} AMS items.")
    print()

    for key, count in summary.most_common():
        print(f"{key}: {count}")


if __name__ == "__main__":
    import_ams()