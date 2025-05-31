import os
import argparse
from PIL import Image


def upscale_image(input_path, output_path, factor, overwrite):
    image = Image.open(input_path)
    width, height = image.size
    new_width = width * factor
    new_height = height * factor

    upscaled_image = image.resize((new_width, new_height), resample=Image.Resampling.NEAREST)

    if overwrite:
        output_path = input_path

    upscaled_image.save(output_path)
    print(
        f"Upscaled {os.path.basename(input_path)} by {factor}x and saved to {output_path}"
    )


def process_input(input_path, output_path, factor, overwrite):
    if os.path.isfile(input_path):
        if os.path.isdir(output_path):
            output_path = os.path.join(
                output_path, f"{os.path.basename(input_path)}"
            )
        upscale_image(input_path, output_path, factor, overwrite)
    elif os.path.isdir(input_path):
        if not os.path.exists(output_path) and not overwrite:
            os.makedirs(output_path)
        for filename in os.listdir(input_path):
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                input_file = os.path.join(input_path, filename)
                if overwrite:
                    output_file = input_file
                else:
                    output_file = os.path.join(output_path, f"{filename}")
                upscale_image(input_file, output_file, factor, overwrite)
    else:
        print(f"Error: {input_path} is not a valid file or directory")


def main():
    parser = argparse.ArgumentParser(
        description="Upscale images using nearest neighbor interpolation"
    )
    parser.add_argument(
        "input", type=str, help="Path to the input file or folder containing images"
    )
    parser.add_argument(
        "output",
        type=str,
        help="Path to the output file or folder (ignored if --overwrite is used)",
    )
    parser.add_argument(
        "factor", type=int, help="Upscale factor (e.g., 2 for 2x upscaling)"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite original images instead of creating new ones",
    )

    args = parser.parse_args()

    process_input(args.input, args.output, args.factor, args.overwrite)


if __name__ == "__main__":
    main()
