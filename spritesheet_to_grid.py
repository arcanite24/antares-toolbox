import os
import argparse
import numpy as np
from PIL import Image
from tqdm import tqdm


def extract_frames(spritesheet_path, frame_width, frame_height):
    """Extract frames from a spritesheet based on fixed frame dimensions."""
    with Image.open(spritesheet_path) as img:
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        
        sheet_width, sheet_height = img.size
        
        # Calculate how many frames we can extract
        frames_x = sheet_width // frame_width
        frames_y = sheet_height // frame_height
        
        frames = []
        
        # Extract each frame
        for y in range(frames_y):
            for x in range(frames_x):
                left = x * frame_width
                upper = y * frame_height
                right = left + frame_width
                lower = upper + frame_height
                
                frame = img.crop((left, upper, right, lower))
                frames.append(frame)
        
        return frames


def create_grid(frames, grid_width, grid_height, output_width=None, output_height=None, bg_color=(128, 128, 128, 255), repeat_frames=False):
    """Arrange frames in a grid of specified dimensions with background color."""
    if not frames:
        raise ValueError("No frames to arrange in grid")
    
    frame_width, frame_height = frames[0].size
    
    # Use input frame dimensions if output dimensions not specified
    output_width = output_width or frame_width
    output_height = output_height or frame_height
    
    # Create an empty grid with the background color
    grid_img = Image.new(
        "RGBA",
        (grid_width * output_width, grid_height * output_height),
        bg_color
    )
    
    # Place frames on the grid
    total_slots = grid_width * grid_height
    
    for i in range(total_slots):
        # If repeating frames is enabled, use modulo to wrap around to the beginning
        # If not repeating and we've run out of frames, stop here
        if i >= len(frames) and not repeat_frames:
            break
        
        # Get the appropriate frame (with wrapping if repeat_frames is True)
        frame_idx = i % len(frames) if repeat_frames else i
        frame = frames[frame_idx]
        
        row = i // grid_width
        col = i % grid_width
        
        # Calculate position to center frame within output dimensions
        x = col * output_width + (output_width - frame_width) // 2
        y = row * output_height + (output_height - frame_height) // 2
        
        grid_img.paste(frame, (x, y), frame)
    
    return grid_img


def process_spritesheet(args):
    """Process a single spritesheet, extract frames and create grid(s)."""
    spritesheet_path, output_dir, frame_width, frame_height, grid_width, grid_height, output_width, output_height, bg_color, repeat_frames = args
    
    try:
        # Extract frames from spritesheet
        frames = extract_frames(spritesheet_path, frame_width, frame_height)
        
        if not frames:
            print(f"Warning: No frames extracted from {spritesheet_path}")
            return
        
        # Calculate how many grids we need (if not repeating frames)
        frames_per_grid = grid_width * grid_height
        grid_count = 1 if repeat_frames else (len(frames) + frames_per_grid - 1) // frames_per_grid
        
        base_filename = os.path.splitext(os.path.basename(spritesheet_path))[0]
        
        # Create each grid
        for grid_index in range(grid_count):
            if repeat_frames:
                # If repeating, use all frames for the single grid
                grid_frames = frames
            else:
                # Otherwise extract the appropriate subset of frames for this grid
                start_idx = grid_index * frames_per_grid
                end_idx = min((grid_index + 1) * frames_per_grid, len(frames))
                grid_frames = frames[start_idx:end_idx]
            
            grid_img = create_grid(grid_frames, grid_width, grid_height, output_width, output_height, bg_color, repeat_frames)
            
            # Save the grid
            output_path = os.path.join(output_dir, f"{base_filename}_grid_{grid_index+1}.png")
            grid_img.save(output_path)
        
        return base_filename, len(frames), grid_count
    
    except Exception as e:
        print(f"Error processing {spritesheet_path}: {str(e)}")
        return None


def parse_color(color_str):
    """Parse color string in format r,g,b,a or r,g,b."""
    try:
        values = [int(x) for x in color_str.split(',')]
        if len(values) == 3:
            values.append(255)  # Add alpha channel if not provided
        
        if len(values) != 4 or any(x < 0 or x > 255 for x in values):
            raise ValueError
        
        return tuple(values)
    except:
        raise argparse.ArgumentTypeError("Color must be r,g,b or r,g,b,a format with values 0-255")


def main():
    parser = argparse.ArgumentParser(description="Extract frames from spritesheets and arrange them on grids")
    
    parser.add_argument(
        "-i", "--input", 
        type=str, 
        required=True,
        help="Input folder containing spritesheets"
    )
    parser.add_argument(
        "-o", "--output", 
        type=str, 
        required=True,
        help="Output folder for grid images"
    )
    parser.add_argument(
        "--frame-width", 
        type=int, 
        required=True,
        help="Width of each frame in the spritesheet"
    )
    parser.add_argument(
        "--frame-height", 
        type=int, 
        required=True,
        help="Height of each frame in the spritesheet"
    )
    parser.add_argument(
        "--output-width",
        type=int,
        default=None,
        help="Width of each frame in the output grid (defaults to frame-width if not specified)"
    )
    parser.add_argument(
        "--output-height",
        type=int,
        default=None,
        help="Height of each frame in the output grid (defaults to frame-height if not specified)"
    )
    parser.add_argument(
        "--grid-width", 
        type=int, 
        required=True,
        help="Number of frames horizontally in the output grid"
    )
    parser.add_argument(
        "--grid-height", 
        type=int, 
        required=True,
        help="Number of frames vertically in the output grid"
    )
    parser.add_argument(
        "--grid-bg-color", 
        type=parse_color, 
        default="128,128,128,255",
        help="Background color for the grid in r,g,b,a format (default: 128,128,128,255)"
    )
    parser.add_argument(
        "--repeat-frames",
        action="store_true",
        help="Repeat frames from the beginning to fill the entire grid"
    )
    
    args = parser.parse_args()
    
    # Ensure input and output directories exist
    if not os.path.isdir(args.input):
        print(f"Error: Input directory '{args.input}' does not exist")
        return
    
    os.makedirs(args.output, exist_ok=True)
    
    # Get all image files from input directory
    spritesheet_files = [
        f for f in os.listdir(args.input) 
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
    ]
    
    if not spritesheet_files:
        print(f"No image files found in {args.input}")
        return
    
    print(f"Found {len(spritesheet_files)} spritesheet files.")
    
    results = []
    for filename in tqdm(spritesheet_files, desc="Processing spritesheets"):
        spritesheet_path = os.path.join(args.input, filename)
        
        process_args = (
            spritesheet_path,
            args.output,
            args.frame_width,
            args.frame_height,
            args.grid_width,
            args.grid_height,
            args.output_width,
            args.output_height,
            args.grid_bg_color,
            args.repeat_frames
        )
        
        result = process_spritesheet(process_args)
        if result:
            results.append(result)
    
    print("\nProcessing complete!")
    print(f"Processed {len(results)} spritesheets.")
    
    for name, frame_count, grid_count in results:
        print(f"  - {name}: {frame_count} frames extracted, {grid_count} grid(s) created")


if __name__ == "__main__":
    main()