import argparse
import os
import shutil
from pathlib import Path
from tqdm import tqdm


def find_images(input_dir: str, extension: str) -> list[Path]:
    """Find all images with given extension recursively"""
    return list(Path(input_dir).rglob(f"*.{extension.lower()}"))


def process_images(images: list[Path], output_dir: str, copy: bool = True) -> None:
    """Copy or move images to output directory"""
    for img in tqdm(images, desc="Processing images"):
        dest = Path(output_dir) / img.name
        try:
            if copy:
                shutil.copy2(img, dest)
            else:
                shutil.move(str(img), str(dest))
        except Exception as e:
            print(f"Error processing {img}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Move or copy images from input directory"
    )
    parser.add_argument("input_dir", help="Input directory to search for images")
    parser.add_argument("output_dir", help="Output directory for images")
    parser.add_argument(
        "extension", help="Image extension to search for (jpg, png, etc)", default="png"
    )
    parser.add_argument("--copy", action="store_true", help="Copy instead of move")

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Find and process images
    images = find_images(args.input_dir, args.extension)
    if not images:
        print(f"No images with extension .{args.extension} found")
        return

    print(f"Found {len(images)} images")
    process_images(images, args.output_dir, args.copy)
    print("Done!")


if __name__ == "__main__":
    main()
