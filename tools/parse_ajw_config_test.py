import re
from pathlib import Path

AJW_ROOT = Path(r"D:\SteamLibrary\steamapps\common\DayZ\!Workshop\@AJs Weapons\addons")


def extract_string(text, field):
    match = re.search(rf'{field}\s*=\s*"([^"]*)"', text)
    return match.group(1).strip() if match else ""


def extract_array(text, field):
    match = re.search(rf'{field}\s*\[\]\s*=\s*\{{(.*?)\}};', text, re.DOTALL)
    if not match:
        return []

    body = match.group(1)
    return re.findall(r'"([^"]+)"', body)


def extract_classnames(text):
    return re.findall(r'class\s+([A-Za-z0-9_]+)\s*:', text)


def main():
    print("Script started")

    configs = list(AJW_ROOT.rglob("config.cpp"))

    print("AJW root:", AJW_ROOT)
    print("Root exists:", AJW_ROOT.exists())
    print("Configs found:", len(configs))

    for config in configs[:10]:
        text = config.read_text(encoding="utf-8", errors="ignore")

        print("\n" + "=" * 80)
        print(config.relative_to(AJW_ROOT))

        print("Display:", extract_string(text, "displayName"))
        print("Description:", extract_string(text, "descriptionShort"))
        print("Model:", extract_string(text, "model"))
        print("Classes:", extract_classnames(text)[:10])
        print("Attachments:", extract_array(text, "attachments"))
        print("Magazines:", extract_array(text, "magazines"))


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()