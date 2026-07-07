import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from database import initialize_database, get_or_create_mod, add_item
from catalog.taxonomy import classify_item


MOD_NAME = "Additional Medical Supplies"
TYPES_PATH = ROOT_DIR / "data" / "imports" / "ams" / "types" / "ams_types.xml"


def import_ams():
    initialize_database()

    if not TYPES_PATH.exists():
        print(f"❌ AMS types file not found: {TYPES_PATH}")
        return

    mod_id = get_or_create_mod(
        name=MOD_NAME,
        author="Unknown",
        type="Medical Mod",
        logo=None,
        description="Additional Medical Supplies mod items.",
    )

    tree = ET.parse(TYPES_PATH)
    root = tree.getroot()

    summary = Counter()
    unclassified = []
    imported = 0
    skipped = 0

    for type_node in root.findall("type"):
        classname = type_node.attrib.get("name")

        if not classname or not classname.startswith("AMS_"):
            skipped += 1
            continue

        category, subcategory = classify_item(
            classname=classname,
            display_name=classname,
            mod_name=MOD_NAME,
        )

        if category == "Miscellaneous":
            unclassified.append(classname)

        add_item(
            classname=classname,
            display_name=classname,
            description=None,
            category=category,
            subcategory=subcategory,
            mod_id=mod_id,
            image=None,
        )

        summary[f"{category} > {subcategory}"] += 1
        imported += 1

    print()
    print("========================================")
    print("Additional Medical Supplies Import")
    print("========================================")
    print(f"Types file: {TYPES_PATH}")
    print(f"Imported AMS items: {imported}")
    print(f"Skipped non-AMS/invalid entries: {skipped}")
    print("----------------------------------------")

    for label, count in summary.most_common():
        print(f"{label}: {count}")

    print("----------------------------------------")
    print("Unclassified items:")

    if unclassified:
        for classname in unclassified:
            print(f" - {classname}")
    else:
        print(" None")

    print("========================================")


if __name__ == "__main__":
    import_ams()