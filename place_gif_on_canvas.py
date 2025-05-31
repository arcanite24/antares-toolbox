#!/usr/bin/env python3
import os
import argparse
import threading
from PIL import Image, ImageSequence
import random
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import time

def parse_args():
    parser = argparse.ArgumentParser(description='Place GIFs on a canvas')
    parser.add_argument('--input', '-i', type=str, required=True, 
                        help='Input folder containing GIF files')
    parser.add_argument('--output', '-o', type=str, default='output',
                        help='Output folder path (default: output)')
    parser.add_argument('--width', '-W', type=int, default=214,
                        help='Canvas width (default: 214)')
    parser.add_argument('--height', '-H', type=int, default=120,
                        help='Canvas height (default: 120)')
    parser.add_argument('--color', '-c', type=str, default='#FF00FF',
                        help='Canvas background color (default: magenta #FF00FF)')
    parser.add_argument('--threads', '-t', type=int, default=4,
                        help='Number of threads to use (default: 4)')
    parser.add_argument('--random', '-r', action='store_true',
                        help='Place GIFs at random positions')
    parser.add_argument('--duration', '-d', type=int, default=100,
                        help='Frame duration in milliseconds (default: 100)')
    return parser.parse_args()

def get_gif_files(input_folder):
    print(f"Looking for GIF files in: {input_folder}")
    gif_files = []
    for file in os.listdir(input_folder):
        if file.lower().endswith('.gif'):
            gif_files.append(os.path.join(input_folder, file))
    print(f"Found {len(gif_files)} GIF files")
    return gif_files

def process_gif(gif_path, canvas_size, bg_color, random_position=False, queue=None):
    try:
        width, height = canvas_size
        print(f"Processing: {os.path.basename(gif_path)}")
        
        # Open the GIF
        gif = Image.open(gif_path)
        
        # Get frames from GIF
        frames = []
        for frame in ImageSequence.Iterator(gif):
            frame = frame.convert('RGBA')
            frames.append(frame.copy())
        
        # Determine position
        if random_position:
            max_x = max(0, width - frames[0].width)
            max_y = max(0, height - frames[0].height)
            position = (random.randint(0, max_x), random.randint(0, max_y))
        else:
            # Center the GIF
            position = ((width - frames[0].width) // 2, (height - frames[0].height) // 2)
        
        print(f"Placing {os.path.basename(gif_path)} at position {position}")
        
        # Create frames with background and GIF
        result_frames = []
        for frame in frames:
            # Create a new background with the specified color
            bg = Image.new('RGBA', (width, height), bg_color)
            # Paste the frame onto the background, using the frame's alpha channel as mask
            bg.paste(frame, position, frame)
            result_frames.append(bg)
        
        if queue:
            queue.put((gif_path, result_frames))
        return gif_path, result_frames
    except Exception as e:
        print(f"Error processing {gif_path}: {e}")
        if queue:
            queue.put((gif_path, None))
        return gif_path, None

def main():
    args = parse_args()
    
    # Validate input folder
    if not os.path.isdir(args.input):
        print(f"Error: Input folder '{args.input}' does not exist.")
        return

    # Create output folder if it doesn't exist
    if not os.path.exists(args.output):
        os.makedirs(args.output)
        print(f"Created output directory: {args.output}")
    elif not os.path.isdir(args.output):
        print(f"Error: Output path '{args.output}' exists but is not a directory.")
        return

    # Get GIF files
    gif_files = get_gif_files(args.input)
    if not gif_files:
        print("No GIF files found in the input folder.")
        return

    canvas_size = (args.width, args.height)
    print(f"Canvas size: {canvas_size}")
    print(f"Background color: {args.color}")
    
    start_time = time.time()
    
    # Process GIFs in parallel
    result_queue = Queue()
    all_frames = {}
    
    print(f"Starting processing with {args.threads} threads")
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = []
        for gif_path in gif_files:
            futures.append(
                executor.submit(
                    process_gif, 
                    gif_path, 
                    canvas_size, 
                    args.color, 
                    args.random,
                    result_queue
                )
            )
        
        # Collect results as they complete
        for _ in range(len(futures)):
            gif_path, frames = result_queue.get()
            if frames:
                all_frames[gif_path] = frames
    
    # Save each processed GIF separately
    if all_frames:
        print(f"Saving {len(all_frames)} processed GIFs...")
        # Inside the save loop, modify the code to:
        for gif_path, frames in all_frames.items():
            # Get the base filename without extension
            base_name = os.path.splitext(os.path.basename(gif_path))[0]
            # Create output filename with .gif extension
            output_file = os.path.join(args.output, f"{base_name}.gif")
            
            print(f"Saving {output_file}...")
            
            # Convert frames to RGB mode to properly show background color
            rgb_frames = [frame.convert('RGB') for frame in frames]
            
            rgb_frames[0].save(
                output_file,
                save_all=True,
                append_images=rgb_frames[1:],
                optimize=False,
                duration=args.duration,
                loop=0,
                disposal=2  # For better transparency handling
            )
        print(f"All GIFs saved to {args.output} directory")
    else:
        print("No valid frames to save.")
    
    elapsed_time = time.time() - start_time
    print(f"Processing completed in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
