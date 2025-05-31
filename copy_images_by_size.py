import argparse
import os
from PIL import Image
import shutil
from tqdm import tqdm


def copy_images_by_size(input_folder, target_size, output_folder):
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Get all files in the input folder
    all_files = [
        f
        for f in os.listdir(input_folder)
        if os.path.isfile(os.path.join(input_folder, f))
    ]

    # Filter for image files (you can expand this list)
    image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp")
    image_files = [f for f in all_files if f.lower().endswith(image_extensions)]

    # Process images
    for image_file in tqdm(image_files, desc="Processing images"):
        input_path = os.path.join(input_folder, image_file)
        try:
            with Image.open(input_path) as img:
                if img.size == target_size:
                    output_path = os.path.join(output_folder, image_file)
                    shutil.copy2(input_path, output_path)
        except Exception as e:
            print(f"Error processing {image_file}: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description="Copy images of a specific size from one folder to another."
    )
    parser.add_argument(
        "input_folder", help="Path to the input folder containing images"
    )
    parser.add_argument(
        "target_size", help="Target size in the format WIDTHxHEIGHT (e.g., 1920x1080)"
    )
    parser.add_argument(
        "output_folder", help="Path to the output folder for copied images"
    )

    args = parser.parse_args()

    # Parse target size
    try:
        width, height = map(int, args.target_size.split("x"))
        target_size = (width, height)
    except ValueError:
        print("Invalid target size format. Use WIDTHxHEIGHT (e.g., 1920x1080)")
        return

    copy_images_by_size(args.input_folder, target_size, args.output_folder)
    print("Image copying complete!")


if __name__ == "__main__":
    main()
