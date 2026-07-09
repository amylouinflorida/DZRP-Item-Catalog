from pathlib import Path

AJW_ROOT = Path(r"D:\SteamLibrary\steamapps\common\DayZ\!Workshop\@AJs Weapons\addons")

def main():
    configs = list(AJW_ROOT.rglob("config.cpp"))

    print(f"Found {len(configs)} config.cpp files:\n")

    for config in configs:
        relative = config.relative_to(AJW_ROOT)
        print(relative)

if __name__ == "__main__":
    main()