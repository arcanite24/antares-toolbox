import os
import argparse
from PIL import Image


def place_images_on_canvas(input_folder, output_folder, canvas_size, canvas_color):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            filepath = os.path.join(input_folder, filename)
            image = Image.open(filepath)

            if image.mode == "RGBA":
                canvas = Image.new("RGBA", canvas_size, canvas_color)
            else:
                canvas = Image.new("RGB", canvas_size, canvas_color)

            image_width, image_height = image.size
            canvas_width, canvas_height = canvas_size

            x_offset = (canvas_width - image_width) // 2
            y_offset = (canvas_height - image_height) // 2

            if image.mode == "RGBA":
                canvas.paste(image, (x_offset, y_offset), mask=image)
            else:
                canvas.paste(image, (x_offset, y_offset))

            output_filepath = os.path.join(output_folder, f"{filename}")
            canvas.save(output_filepath)

            print(
                f"Placed {filename} on a {canvas_width}x{canvas_height} {canvas_color} canvas and saved to {output_filepath}"
            )


def main():
    parser = argparse.ArgumentParser(description="Place images on a canvas")
    parser.add_argument(
        "input_folder", type=str, help="Path to the input folder containing images"
    )
    parser.add_argument(
        "output_folder",
        type=str,
        help="Path to the output folder to save canvas images",
    )
    parser.add_argument(
        "--canvas-size",
        type=int,
        nargs=2,
        default=[64, 64],
        help="Size of the canvas (width height), default is 64x64",
    )
    parser.add_argument(
        "--canvas-color",
        type=str,
        default="white",
        help="Color of the canvas, default is white",
    )

    args = parser.parse_args()

    place_images_on_canvas(
        args.input_folder,
        args.output_folder,
        tuple(args.canvas_size),
        args.canvas_color,
    )


if __name__ == "__main__":
    main()
