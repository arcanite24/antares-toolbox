import os
import argparse
from PIL import Image


def downscale_images(input_folder, output_folder, factor, output_extension=".png"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".ico")):
            filepath = os.path.join(input_folder, filename)
            image = Image.open(filepath)

            width, height = image.size
            new_width = width // factor
            new_height = height // factor

            downscaled_image = image.resize(
                (new_width, new_height), resample=Image.Resampling.NEAREST
            )

            output_filename = (
                f"{os.path.splitext(filename)[0]}{output_extension}"
            )
            output_filepath = os.path.join(output_folder, output_filename)
            downscaled_image.save(output_filepath)

            print(f"Downscaled {filename} by {factor}x and saved to {output_filepath}")


def main():
    parser = argparse.ArgumentParser(
        description="Downscale images using nearest neighbor interpolation"
    )
    parser.add_argument(
        "input_folder", type=str, help="Path to the input folder containing images"
    )
    parser.add_argument(
        "output_folder",
        type=str,
        help="Path to the output folder to save downscaled images",
    )
    parser.add_argument(
        "factor", type=int, help="Downscale factor (e.g., 2 for 2x downscaling)"
    )
    parser.add_argument(
        "--output_extension",
        type=str,
        default=".png",
        help="Output file extension (default: .png)",
    )

    args = parser.parse_args()

    downscale_images(
        args.input_folder, args.output_folder, args.factor, args.output_extension
    )


if __name__ == "__main__":
    main()
