import argparse
from PIL import Image
import os


def create_image_grid(
    input_folder,
    output_path,
    grid_width,
    grid_height,
    padding,
    final_size,
    background_color="#FFFFFF",
):
    images = [
        Image.open(os.path.join(input_folder, img))
        for img in os.listdir(input_folder)
        if img.endswith(("png", "jpg", "jpeg"))
    ]

    # Calculate single image size based on final dimensions, grid size, and padding
    single_width = (final_size[0] - (padding * (grid_width + 1))) // grid_width
    single_height = (final_size[1] - (padding * (grid_height + 1))) // grid_height

    # Create a new image with a white background
    grid_image = Image.new("RGB", final_size, color=background_color)

    x_offset, y_offset = padding, padding
    for i, img in enumerate(images[: grid_width * grid_height]):
        img = img.resize((single_width, single_height), Image.ANTIALIAS)
        grid_image.paste(img, (x_offset, y_offset))
        x_offset += single_width + padding
        if (i + 1) % grid_width == 0:
            x_offset = padding
            y_offset += single_height + padding

    grid_image.save(output_path)
    print(f"Grid image saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an image grid.")
    parser.add_argument(
        "--input-folder", type=str, required=True, help="Folder containing images."
    )
    parser.add_argument(
        "--output-path", type=str, required=True, help="Output path for the image grid."
    )
    parser.add_argument(
        "--grid-width",
        type=int,
        required=True,
        help="Number of images in the grid's width.",
    )
    parser.add_argument(
        "--grid-height",
        type=int,
        required=True,
        help="Number of images in the grid's height.",
    )
    parser.add_argument(
        "--padding", type=int, required=True, help="Padding between images (in pixels)."
    )
    parser.add_argument(
        "--final-size",
        type=int,
        nargs=2,
        required=True,
        help="Final image size (width height).",
    )
    parser.add_argument(
        "--background-color",
        type=str,
        default="#FFFFFF",
        help="Background color (hex).",
    )

    args = parser.parse_args()

    create_image_grid(
        args.input_folder,
        args.output_path,
        args.grid_width,
        args.grid_height,
        args.padding,
        args.final_size,
        args.background_color,
    )

# python fancy_grid.py --input-folder cascade\pixelcascade128-v2\raw_selected --output-path cascade\pixelcascade128-v2\grid128.png --grid-width 3 --grid-height 3 --padding 8 --final-size 1024 1024