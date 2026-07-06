def classify_item(classname):
    name = classname.lower()

    # ---------- WEAPONS / AMMO / ATTACHMENTS ----------

    if "ammo_box" in name or "ammobox" in name:
        return "Weapons", "Ammunition", "Ammo Box"

    if "ammo" in name:
        return "Weapons", "Ammunition", "Ammo"

    if "mag_" in name or "_mag_" in name or "magazine" in name:
        return "Weapons", "Magazines", "Magazine"

    if any(word in name for word in [
        "optic", "scope", "sight", "acog", "eotech", "elcan", "microt2", "pso", "kashtan"
    ]):
        return "Weapons", "Attachments", "Optic"

    if any(word in name for word in [
        "suppressor", "silencer"
    ]):
        return "Weapons", "Attachments", "Suppressor"

    if any(word in name for word in [
        "hndgrd", "handguard", "_hg"
    ]):
        return "Weapons", "Attachments", "Handguard"

    if any(word in name for word in [
        "foregrip", "_fg_", "bipod", "grip"
    ]):
        return "Weapons", "Attachments", "Grip / Bipod"

    if any(word in name for word in [
        "bttstock", "buttstock", "stock"
    ]):
        return "Weapons", "Attachments", "Stock"

    if any(word in name for word in [
        "laser", "peq", "dbal", "ngal", "mawl", "gunlight", "flashlight"
    ]):
        return "Weapons", "Attachments", "Light / Laser"

    if any(word in name for word in [
        "knife", "machete", "axe", "hatchet", "sword", "bat", "crowbar"
    ]):
        return "Weapons", "Melee", "Melee Weapon"

    if classname.startswith("AJW_"):
        return "Weapons", "Firearms", "Firearm"

    # ---------- MEDICAL ----------

    if any(word in name for word in [
        "bandage", "saline", "blood", "morphine", "epinephrine", "pill",
        "vitamin", "splint", "medical", "firstaid", "syringe", "iv"
    ]):
        return "Medical", "Medical Supplies", "Medical"

    # ---------- FOOD / DRINK ----------

    if any(word in name for word in [
        "can", "food", "meat", "fruit", "drink", "water", "soda", "canteen", "bottle"
    ]):
        return "Food & Drink", "Food & Drink", "Consumable"

    # ---------- CLOTHING ----------

    if any(word in name for word in ["hat", "cap", "helmet", "beanie"]):
        return "Clothing", "Headwear", "Hat / Helmet"

    if any(word in name for word in ["shirt", "jacket", "coat", "hoodie"]):
        return "Clothing", "Tops", "Shirt / Jacket"

    if any(word in name for word in ["pants", "trousers", "jeans"]):
        return "Clothing", "Pants", "Pants"

    if any(word in name for word in ["boots", "shoes", "sneakers"]):
        return "Clothing", "Footwear", "Shoes"

    if "glove" in name:
        return "Clothing", "Gloves", "Gloves"

    if any(word in name for word in ["vest", "platecarrier", "carrier"]):
        return "Clothing", "Vests", "Vest"

    if any(word in name for word in ["backpack", "bag"]):
        return "Clothing", "Backpacks", "Backpack"

    # ---------- TOOLS ----------

    if any(word in name for word in [
        "screwdriver", "wrench", "hammer", "pliers", "shovel", "pickaxe",
        "saw", "tool", "repairkit", "ducttape"
    ]):
        return "Tools", "Tools", "Tool"

    # ---------- VEHICLES ----------

    if any(word in name for word in [
        "wheel", "tire", "battery", "sparkplug", "radiator", "door", "hood",
        "trunk", "car", "truck", "vehicle"
    ]):
        return "Vehicle Parts", "Vehicle Parts", "Vehicle Part"

    # ---------- BASE BUILDING ----------

    if any(word in name for word in [
        "fence", "wall", "gate", "storage", "crate", "barrel", "tent",
        "lock", "code", "plank", "nail", "metalwire"
    ]):
        return "Base Building", "Base Building", "Base Building"

    # ---------- ELECTRONICS ----------

    if any(word in name for word in [
        "radio", "battery", "charger", "gps", "transmitter", "electronic"
    ]):
        return "Electronics", "Electronics", "Electronics"

    return "Miscellaneous", "Miscellaneous", "Miscellaneous"