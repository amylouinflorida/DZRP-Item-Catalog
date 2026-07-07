import sqlite3
import xml.etree.ElementTree as ET

from database import add_item

MOD_NAME = "Additional Medical Supplies"

tree = ET.parse("additional medical supplies types.txt")
root = tree.getroot()

count = 0

for item in root.findall("type"):

    classname = item.attrib["name"]

    display_name = (
        classname
        .replace("AMS_", "")
        .replace("_", " ")
    )

    add_item(
        classname=classname,
        display_name=display_name,
        mod_id=2      # we'll fix this next
    )

    count += 1

print(f"Imported {count} AMS items.")