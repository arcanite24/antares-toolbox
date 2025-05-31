import os
import argparse
from PIL import Image


def quantize_images(input_folder, output_folder, color_limit):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            filepath = os.path.join(input_folder, filename)
            image = Image.open(filepath)

            quantized_image = image.quantize(colors=color_limit, method=Image.MEDIANCUT)

            output_filepath = os.path.join(output_folder, f"quantized_{filename}")
            quantized_image.save(output_filepath)

            print(
                f"Quantized {filename} to {color_limit} colors and saved to {output_filepath}"
            )


def main():
    parser = argparse.ArgumentParser(description="Quantize images for pixel art")
    parser.add_argument(
        "input_folder", type=str, help="Path to the input folder containing images"
    )
    parser.add_argument(
        "output_folder",
        type=str,
        help="Path to the output folder to save quantized images",
    )
    parser.add_argument(
        "color_limit", type=int, help="Maximum number of colors in the quantized image"
    )

    args = parser.parse_args()

    quantize_images(args.input_folder, args.output_folder, args.color_limit)


if __name__ == "__main__":
    main()
