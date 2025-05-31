import os
import argparse
import shutil
from tqdm import tqdm
from PIL import Image, ImageFile


def is_image_corrupted(image_path):
    try:
        with Image.open(image_path) as img:
            img.load()
    except (IOError, OSError) as e:
        if "image file is truncated" in str(e):
            return True
    return False


def move_corrupted_files(input_folder, output_folder):
    corrupted_folder = os.path.join(output_folder, "corrupted")
    os.makedirs(corrupted_folder, exist_ok=True)

    total_files = sum(1 for _ in os.listdir(input_folder))

    with tqdm(total=total_files, unit="file", desc="Processing files") as progress_bar:
        for filename in os.listdir(input_folder):
            if filename.endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif")):
                image_path = os.path.join(input_folder, filename)
                txt_path = os.path.splitext(image_path)[0] + ".txt"

                if is_image_corrupted(image_path):
                    print(f"Moving corrupted image: {filename}")
                    shutil.move(image_path, corrupted_folder)

                    if os.path.exists(txt_path):
                        print(
                            f"Moving corresponding .txt file: {os.path.basename(txt_path)}"
                        )
                        shutil.move(txt_path, corrupted_folder)

            progress_bar.update(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Move corrupted image files and their corresponding .txt files."
    )
    parser.add_argument(
        "input_folder", help="Path to the input folder containing the image files."
    )
    parser.add_argument(
        "output_folder",
        help="Path to the output folder where corrupted files will be moved.",
    )
    args = parser.parse_args()

    ImageFile.LOAD_TRUNCATED_IMAGES = True

    move_corrupted_files(args.input_folder, args.output_folder)
