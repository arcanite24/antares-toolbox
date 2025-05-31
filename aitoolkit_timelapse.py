import os
from PIL import Image, ImageDraw, ImageFont
import argparse
import concurrent.futures
import multiprocessing


def add_label(image_path, step):
    """Add a label with the step number to the image."""
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Load a larger, bold font
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust the path if needed
    font = ImageFont.truetype(font_path, 36)  # Use a larger font size

    # Prepare the label text
    label = f"Step {step}"

    # Calculate text size using textbbox
    bbox = draw.textbbox((0, 0), label, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Define position for the text (anchored to the right)
    x = image.width - text_width - 10  # 10 pixels from the right edge
    y = image.height - text_height - 10  # 10 pixels from the bottom edge

    # Draw a black rectangle behind the text with some padding
    padding = 5
    draw.rectangle(
        [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
        fill="black",
    )

    # Draw the text in white, aligned to the right
    draw.text((x, y), label, font=font, fill="white")

    return image


def process_images(file_step_pairs):
    images = []
    for file, step in file_step_pairs:
        image_with_label = add_label(file, step)
        images.append(image_with_label)
    return images


def create_gif(input_folder, output_file, duration=500):
    # Dictionary to hold images for each sample group
    sample_groups = {}

    # Iterate over all files in the input folder
    for filename in sorted(os.listdir(input_folder)):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            # Split the filename to isolate the sample group
            parts = filename.split("__")[1].split("_")
            step = str(int(parts[0]))  # Truncate leading zeros
            sample_group = parts[1]  # This is the last part (e.g., '0', '1', etc.)

            if sample_group not in sample_groups:
                sample_groups[sample_group] = []
            sample_groups[sample_group].append(
                (os.path.join(input_folder, filename), step)
            )

    # Process images using multithreading
    max_cores = multiprocessing.cpu_count() - 1  # Use max cores minus 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_cores) as executor:
        for sample_group, files in sample_groups.items():
            # Process images in parallel
            future = executor.submit(process_images, files)
            images = future.result()

            # Save the images as a GIF
            images[0].save(
                f"{output_file}_group_{sample_group}.gif",
                save_all=True,
                append_images=images[1:],
                duration=duration,
                loop=0,
            )
            print(
                f"GIF saved for group {sample_group} as {output_file}_group_{sample_group}.gif"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a GIF from training samples.")
    parser.add_argument("input_folder", help="Input folder containing the images.")
    parser.add_argument("output_file", help="Base name for the output GIF files.")
    parser.add_argument(
        "--duration", type=int, default=500, help="Duration per image in milliseconds."
    )

    args = parser.parse_args()

    create_gif(args.input_folder, args.output_file, args.duration)
