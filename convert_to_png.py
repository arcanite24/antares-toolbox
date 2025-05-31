import os
import argparse
import logging
from PIL import Image
from tqdm import tqdm


def convert_to_png(input_folder, overwrite):
    # Define a list of common image extensions
    image_extensions = ('.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')
    
    files = [
        f for f in os.listdir(input_folder)
        if os.path.isfile(os.path.join(input_folder, f)) and 
        f.lower().endswith(image_extensions)
    ]

    with tqdm(total=len(files), desc="Converting images") as pbar:
        for filename in files:
            file_path = os.path.join(input_folder, filename)
            try:
                with Image.open(file_path) as img:
                    name, ext = os.path.splitext(filename)
                    new_filename = f"{name}.png"
                    new_file_path = os.path.join(input_folder, new_filename)

                    img.save(new_file_path, "PNG")
                    logging.info(f"Converted: {filename} -> {new_filename}")

                    if overwrite and ext.lower() != ".png":
                        os.remove(file_path)
                        logging.info(f"Removed original file: {filename}")
            except (IOError, OSError):
                logging.warning(f"Skipped: {filename} (not a valid image file)")

            pbar.update(1)


def main():
    parser = argparse.ArgumentParser(description="Convert images to PNG format")
    parser.add_argument(
        "input_folder", help="Path to the input folder containing images"
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite original files"
    )
    parser.add_argument(
        "--log",
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Set the logging level",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=args.log.upper(), format="%(asctime)s - %(levelname)s - %(message)s"
    )

    if not os.path.isdir(args.input_folder):
        logging.error(f"Error: {args.input_folder} is not a valid directory")
        return

    logging.info(f"Starting conversion in folder: {args.input_folder}")
    convert_to_png(args.input_folder, args.overwrite)
    logging.info("Conversion completed")


if __name__ == "__main__":
    main()