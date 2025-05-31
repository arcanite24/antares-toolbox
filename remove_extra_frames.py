import os
import argparse
import shutil
import re
from tqdm import tqdm


def remove_extra_frames(input_folder):
    print(f"Processing folder: {input_folder}")

    # Create the "removed" subfolder if it doesn't exist
    removed_folder = os.path.join(input_folder, "removed")
    os.makedirs(removed_folder, exist_ok=True)
    print(f"Created 'removed' folder: {removed_folder}")

    # Regular expression to match frame filenames
    frame_pattern = re.compile(r"(.+)_frame_(\d{3})\..*")

    # Dictionary to keep track of animations and their frames
    animations = {}

    # Iterate through files in the input folder
    print("Scanning files and identifying animations...")
    for filename in tqdm(os.listdir(input_folder), desc="Scanning files"):
        match = frame_pattern.match(filename)
        if match:
            animation_name, frame_number = match.groups()
            if animation_name not in animations:
                animations[animation_name] = []
            animations[animation_name].append(filename)

    print(f"Found {len(animations)} animations to process")

    # Process each animation
    for animation_name, frames in tqdm(
        animations.items(), desc="Processing animations"
    ):
        # Sort frames by frame number
        frames.sort(key=lambda x: int(frame_pattern.match(x).group(2)))

        # Keep the first frame, move the rest to the "removed" folder
        for frame in frames[1:]:
            src = os.path.join(input_folder, frame)
            dst = os.path.join(removed_folder, frame)
            shutil.move(src, dst)

        print(f"Processed animation: {animation_name} ({len(frames)} frames)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove extra frames from animations in a folder."
    )
    parser.add_argument("input_folder", help="Path to the folder containing images")
    args = parser.parse_args()

    remove_extra_frames(args.input_folder)
    print("Done processing animations.")
