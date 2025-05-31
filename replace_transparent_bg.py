import os
import sys
from PIL import Image


def replace_transparent_background(
    input_folder, output_folder, bg_color=(255, 255, 255)
):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(
            (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")
        ):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path).convert("RGBA")
            new_img = Image.new("RGBA", img.size, bg_color)
            new_img.paste(img, (0, 0), img)
            new_img = new_img.convert("RGB")  # Convert back to non-alpha mode
            output_path = os.path.join(output_folder, filename)
            new_img.save(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python replace_bg.py <input_folder> <output_folder> [background_color]"
        )
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    bg_color = (255, 255, 255)  # default white

    if len(sys.argv) == 4:
        color_str = sys.argv[3]
        bg_color = tuple(map(int, color_str.split(",")))

    replace_transparent_background(input_folder, output_folder, bg_color)
    print(f"Processed images saved to {output_folder}")
