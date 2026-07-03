from PIL import Image
from pathlib import Path

INPUT_FOLDER = Path("extracted_icons")
OUTPUT_FOLDER = Path("catalog_images")

OUTPUT_SIZE = 256
PADDING = 24

OUTPUT_FOLDER.mkdir(exist_ok=True)

for file in INPUT_FOLDER.glob("*.png"):
    print(f"Processing {file.name}")

    img = Image.open(file).convert("RGBA")

    # Remove empty transparent space
    bbox = img.getbbox()

    if not bbox:
        continue

    img = img.crop(bbox)

    # Resize while keeping proportions
    max_size = OUTPUT_SIZE - (PADDING * 2)

    img.thumbnail((max_size, max_size), Image.LANCZOS)

    # Create transparent canvas
    canvas = Image.new(
        "RGBA",
        (OUTPUT_SIZE, OUTPUT_SIZE),
        (255, 255, 255, 0)
    )

    # Center image
    x = (OUTPUT_SIZE - img.width) // 2
    y = (OUTPUT_SIZE - img.height) // 2

    canvas.paste(img, (x, y), img)

    output_path = OUTPUT_FOLDER / file.name
    canvas.save(output_path)

print("Done!")