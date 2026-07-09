from pathlib import Path
import shutil

# Change this to the folder where your AJW PBOs are extracted
SOURCE_DIR = Path(r"D:\AJW_EXTRACTED")

# Where we will collect copied configs
OUTPUT_DIR = Path("data/imports/ajw_weapon_configs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

count = 0

for config_path in SOURCE_DIR.rglob("config.cpp"):
    relative_path = config_path.relative_to(SOURCE_DIR)

    # Only grab firearm/pistol weapon configs for now
    relative_text = str(relative_path).replace("\\", "/")

    if not (
        "AJW_Firearms_AssaultRifles" in relative_text
        or "AJW_Firearms_Rifles" in relative_text
        or "AJW_Firearms_SMG" in relative_text
        or "AJW_Firearms_Shotgun" in relative_text
        or "AJW_Firearms_Snipers" in relative_text
        or "AJW_Firearms_LMG" in relative_text
        or "AJW_Pistols" in relative_text
    ):
        continue

    safe_name = "_".join(relative_path.parts[:-1]) + "_config.cpp"
    destination = OUTPUT_DIR / safe_name

    shutil.copy2(config_path, destination)

    print(f"Copied: {relative_path}")

    count += 1

print(f"\nDone. Copied {count} weapon config file(s).")