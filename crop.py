import os
import argparse
from PIL import Image


def crop_images(input_folder, output_folder, width, height, x_offset, y_offset):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            image_path = os.path.join(input_folder, filename)
            image = Image.open(image_path)

            cropped_image = image.crop(
                (x_offset, y_offset, x_offset + width, y_offset + height)
            )

            output_path = os.path.join(output_folder, filename)
            cropped_image.save(output_path)

            print(f"Cropped {filename} and saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Crop images in a folder")
    parser.add_argument(
        "input_folder", help="Path to the input folder containing images"
    )
    parser.add_argument(
        "output_folder", help="Path to the output folder for saving cropped images"
    )
    parser.add_argument("width", type=int, help="Width of the cropped image")
    parser.add_argument("height", type=int, help="Height of the cropped image")
    parser.add_argument("x_offset", type=int, help="X-offset for cropping")
    parser.add_argument("y_offset", type=int, help="Y-offset for cropping")

    args = parser.parse_args()

    crop_images(
        args.input_folder,
        args.output_folder,
        args.width,
        args.height,
        args.x_offset,
        args.y_offset,
    )


if __name__ == "__main__":
    main()
