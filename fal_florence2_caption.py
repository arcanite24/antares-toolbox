import os
import argparse
from dotenv import load_dotenv
import fal_client
from tqdm import tqdm
import shutil
import time
import base64
import concurrent.futures

# Load environment variables
load_dotenv()


def caption_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode("utf-8")
            image_url = f"data:image/png;base64,{base64_image}"

        handler = fal_client.submit(
            "fal-ai/florence-2-large/detailed-caption",
            arguments={"image_url": image_url},
        )
        result = handler.get()
        return result["results"]
    except Exception as e:
        print(f"Error captioning {image_path}: {str(e)}")
        return None


def process_images(input_folder, max_workers=5):
    failed_folder = os.path.join(input_folder, "failed")
    os.makedirs(failed_folder, exist_ok=True)

    image_files = [
        f
        for f in os.listdir(input_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
    ]

    print(f"Found {len(image_files)} images to process.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for image_file in image_files:
            image_path = os.path.join(input_folder, image_file)
            futures.append(
                executor.submit(process_single_image, image_path, failed_folder)
            )

        for future in tqdm(
            concurrent.futures.as_completed(futures),
            total=len(futures),
            desc="Processing images",
        ):
            future.result()


def process_single_image(image_path, failed_folder):
    image_file = os.path.basename(image_path)
    txt_path = os.path.splitext(image_path)[0] + ".txt"

    retries = 3
    while retries > 0:
        caption = caption_image(image_path)
        if caption:
            with open(txt_path, "w") as f:
                f.write(caption)
            return
        else:
            retries -= 1
            if retries > 0:
                print(f"Retrying {image_file}... ({retries} attempts left)")
                time.sleep(2)  # Wait for 2 seconds before retrying

    print(f"Failed to caption {image_file} after 3 attempts. Moving to failed folder.")
    shutil.move(image_path, os.path.join(failed_folder, image_file))


def main():
    parser = argparse.ArgumentParser(
        description="Caption images using FAL Florence-2 model"
    )
    parser.add_argument("input_folder", help="Path to the folder containing images")
    parser.add_argument(
        "--workers", type=int, default=5, help="Number of parallel tasks (default: 5)"
    )
    args = parser.parse_args()

    if not os.path.isdir(args.input_folder):
        print(f"Error: {args.input_folder} is not a valid directory")
        return

    print("Starting image captioning process...")
    process_images(args.input_folder, max_workers=args.workers)
    print("Image captioning process completed.")


if __name__ == "__main__":
    main()
