#!/usr/bin/env python3

import argparse
from PIL import Image
import imageio
import numpy as np
import os
from typing import Tuple


def parse_grid_size(grid_size: str) -> Tuple[int, int]:
    """Parse the grid size string (e.g., '4x4') into a tuple of integers."""
    try:
        rows, cols = map(int, grid_size.lower().split("x"))
        return rows, cols
    except ValueError:
        raise ValueError("Grid size must be in format 'NxN', e.g., '4x4'")


def get_output_path(input_path: str) -> str:
    """Generate output path based on input path."""
    base_path = os.path.splitext(input_path)[0]
    return f"{base_path}_split.gif"


def is_blank_frame(image: Image.Image, threshold: float = 0.05) -> bool:
    """
    Check if an image is mostly blank/empty.

    Args:
        image: PIL Image object
        threshold: Standard deviation threshold (0-1) to determine blankness

    Returns:
        bool: True if the image is considered blank
    """
    # Convert to grayscale and numpy array
    gray_image = np.array(image.convert("L"))

    # Calculate standard deviation and normalize
    std_dev = np.std(gray_image) / 255.0

    return std_dev < threshold


def split_image(
    image_path: str,
    grid_size: Tuple[int, int],
    skip_blank: bool = False,
    blank_threshold: float = 0.05,
) -> list:
    """Split the image into a grid and return list of image pieces."""
    with Image.open(image_path) as img:
        # Convert to RGB if necessary
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Get image dimensions
        width, height = img.size
        rows, cols = grid_size

        # Calculate tile dimensions
        tile_width = width // cols
        tile_height = height // rows

        # Store image pieces
        pieces = []

        # Split image into grid
        for i in range(rows):
            for j in range(cols):
                left = j * tile_width
                upper = i * tile_height
                right = left + tile_width
                lower = upper + tile_height

                # Crop piece
                piece = img.crop((left, upper, right, lower))

                # Only add non-blank pieces if skip_blank is True
                if not skip_blank or not is_blank_frame(piece, blank_threshold):
                    pieces.append(piece)

        if not pieces:
            raise ValueError(
                "No non-blank pieces found in the image. Try adjusting the blank threshold."
            )

        return pieces


def create_gif(
    pieces: list, output_path: str, duration: float = 0.3, loop: bool = True
):
    """Create a GIF from the image pieces."""
    # Convert PIL images to numpy arrays
    frames = [np.array(img) for img in pieces]

    # Save as GIF
    imageio.mimsave(
        output_path,
        frames,
        duration=duration,
        loop=0 if loop else 1,  # 0 means loop forever, 1 means play once
    )


def main():
    parser = argparse.ArgumentParser(
        description="Split an image into a grid and create a GIF"
    )
    parser.add_argument("image", help="Path to the input image")
    parser.add_argument("--grid", default="4x4", help="Grid size (e.g., 4x4, 10x10)")
    parser.add_argument(
        "--duration", type=float, default=0.5, help="Duration for each frame in seconds"
    )
    parser.add_argument(
        "--output", help="Output GIF path (defaults to input_split.gif)"
    )
    parser.add_argument("--no-loop", action="store_true", help="Disable GIF looping")
    parser.add_argument(
        "--skip-blank", action="store_true", help="Skip mostly blank frames"
    )
    parser.add_argument(
        "--blank-threshold",
        type=float,
        default=0.05,
        help="Threshold for determining blank frames (0-1, default: 0.05)",
    )

    args = parser.parse_args()

    try:
        # Parse grid size
        grid_size = parse_grid_size(args.grid)

        # Validate blank threshold
        if not 0 <= args.blank_threshold <= 1:
            raise ValueError("Blank threshold must be between 0 and 1")

        # Determine output path
        output_path = args.output if args.output else get_output_path(args.image)

        # Split image into pieces
        pieces = split_image(
            args.image, grid_size, args.skip_blank, args.blank_threshold
        )

        # Create GIF
        create_gif(pieces, output_path, args.duration, not args.no_loop)

        print(f"Successfully created GIF at {output_path}")
        print(f"Number of frames in GIF: {len(pieces)}")

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
