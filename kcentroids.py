import argparse
import os
from PIL import Image
import numpy as np
from itertools import product
from tqdm import tqdm
import multiprocessing as mp
import cv2


def kCentroid(image, width, height, centroids):
    # Convert image to numpy array for faster processing
    img_array = np.array(image.convert("RGB"))

    # Create an empty array for the downscaled image
    downscaled = np.zeros((height, width, 3), dtype=np.uint8)

    # Calculate the scaling factors
    wFactor = image.width / width
    hFactor = image.height / height

    # Iterate over each tile in the downscaled image
    for x, y in product(range(width), range(height)):
        # Extract the tile from the numpy array
        tile = img_array[int(y*hFactor):int((y+1)*hFactor), int(x*wFactor):int((x+1)*wFactor)]

        # Reshape the tile for k-means
        pixels = tile.reshape(-1, 3)

        # Perform k-means clustering
        _, labels, centers = cv2.kmeans(np.float32(pixels), centroids, None, criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0), attempts=10, flags=cv2.KMEANS_RANDOM_CENTERS)

        # Find the most common label
        most_common_label = np.bincount(labels.flatten()).argmax()

        # Assign the most common color to the corresponding pixel in the downscaled image
        downscaled[y, x, :] = centers[most_common_label].astype(np.uint8)

    return Image.fromarray(downscaled, mode="RGB")


def process_image(args):
    input_path, output_path, width, height, centroids, show = args
    image = Image.open(input_path)
    result = kCentroid(image, width, height, centroids)
    result.save(output_path)
    if show:
        result.show()


def main():
    parser = argparse.ArgumentParser(
        description="Apply kCentroid to an image or a folder of images."
    )
    parser.add_argument("input", help="Input image file or folder")
    parser.add_argument("output", help="Output image file or folder")
    parser.add_argument(
        "--width", type=int, required=True, help="Width of the downscaled image",
        default=256
    )
    parser.add_argument(
        "--height", type=int, required=True, help="Height of the downscaled image",
        default=256
    )
    parser.add_argument(
        "--centroids",
        type=int,
        required=True,
        help="Number of centroids for k-means clustering",
        default=2
    )
    parser.add_argument("--show", action="store_true", help="Show the resulting image")
    parser.add_argument("-o", "--override", action="store_true", help="Process all images even if they already exist in the output folder")

    args = parser.parse_args()

    if os.path.isdir(args.input):
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        
        image_files = [f for f in os.listdir(args.input) if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))]
        
        # Prepare arguments for multiprocessing
        process_args = []
        for f in image_files:
            output_path = os.path.join(args.output, f)
            if args.override or not os.path.exists(output_path):
                process_args.append((os.path.join(args.input, f), output_path, args.width, args.height, args.centroids, args.show))

        # Use multiprocessing to process images in parallel
        with mp.Pool(processes=mp.cpu_count()) as pool:
            list(tqdm(pool.imap(process_image, process_args), total=len(process_args), desc="Processing images"))
    else:
        process_image((args.input, args.output, args.width, args.height, args.centroids, args.show))


if __name__ == "__main__":
    main()
