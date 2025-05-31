import os
import cv2
import argparse
import numpy as np
import logging
from tqdm import tqdm
from multiprocessing import Pool, cpu_count


def process_spritesheet(args):
    spritesheet_path, output_dir, draw_bounding_boxes, padding = args
    spritesheet = cv2.imread(spritesheet_path)
    original = spritesheet.copy()
    gray = cv2.cvtColor(spritesheet, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    dilate = cv2.dilate(close, kernel, iterations=1)

    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    sprite_number = 0
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)

        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(spritesheet.shape[1] - x, w + 2 * padding)
        h = min(spritesheet.shape[0] - y, h + 2 * padding)

        ROI = original[y : y + h, x : x + w]
        output_path = os.path.join(
            output_dir,
            f"sprite_{os.path.basename(spritesheet_path)}_{sprite_number}.png",
        )
        cv2.imwrite(output_path, ROI)
        sprite_number += 1

    if draw_bounding_boxes:
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)

            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(spritesheet.shape[1] - x, w + 2 * padding)
            h = min(spritesheet.shape[0] - y, h + 2 * padding)

            cv2.rectangle(spritesheet, (x, y), (x + w, y + h), (36, 255, 12), 2)

        bounding_box_dir = os.path.join(output_dir, "bounding_boxes")
        os.makedirs(bounding_box_dir, exist_ok=True)
        bounding_box_path = os.path.join(
            bounding_box_dir, f"bounding_boxes_{os.path.basename(spritesheet_path)}"
        )
        cv2.imwrite(bounding_box_path, spritesheet)


def main():
    parser = argparse.ArgumentParser(description="Spritesheet Slicer")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input folder containing spritesheets",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Output folder for sliced images",
    )
    parser.add_argument(
        "-b",
        "--bounding-boxes",
        action="store_true",
        help="Save images with bounding boxes",
    )
    parser.add_argument(
        "-p",
        "--padding",
        type=int,
        default=0,
        help="Padding size for bounding boxes (default: 0)",
    )
    parser.add_argument(
        "-c",
        "--cores",
        type=int,
        default=1,
        help="Number of CPU cores to use (default: 1)",
    )
    args = parser.parse_args()

    input_folder = args.input
    output_folder = args.output
    draw_bounding_boxes = args.bounding_boxes
    padding = args.padding
    num_cores = args.cores

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    os.makedirs(output_folder, exist_ok=True)

    spritesheet_files = [
        f for f in os.listdir(input_folder) if f.endswith(".png") or f.endswith(".jpg")
    ]

    logging.info(f"Found {len(spritesheet_files)} spritesheet files.")

    pool = Pool(processes=num_cores)
    process_args = [
        (
            os.path.join(input_folder, filename),
            output_folder,
            draw_bounding_boxes,
            padding,
        )
        for filename in spritesheet_files
    ]
    list(
        tqdm(pool.imap(process_spritesheet, process_args), total=len(spritesheet_files))
    )
    pool.close()
    pool.join()

    logging.info("Spritesheet slicing completed.")


if __name__ == "__main__":
    main()
