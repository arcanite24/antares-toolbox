import os
import argparse
import concurrent.futures
from PIL import Image
import imageio
import tempfile
import shutil
from upscale import upscale_image


def extract_gif_frames(gif_path, temp_dir, upscale_factor=None):
    """Extract frames from a GIF and optionally upscale them"""
    gif = Image.open(gif_path)
    frames = []
    frame_paths = []
    
    try:
        for i in range(0, gif.n_frames):
            gif.seek(i)
            frame = gif.convert('RGB')
            frame_path = os.path.join(temp_dir, f"frame_{i:05d}.png")
            
            if upscale_factor and upscale_factor > 1:
                # Save temporarily to upscale
                temp_frame_path = os.path.join(temp_dir, f"temp_frame_{i:05d}.png")
                frame.save(temp_frame_path)
                upscale_image(temp_frame_path, frame_path, upscale_factor, False)
                os.remove(temp_frame_path)
            else:
                frame.save(frame_path)
            
            frame_paths.append(frame_path)
            
    except EOFError:
        pass
    
    return frame_paths, gif.info.get('duration', 100)


def convert_gif_to_video(gif_path, output_path, upscale_factor=None):
    """Convert a GIF to an MP4 video with optional upscaling"""
    with tempfile.TemporaryDirectory() as temp_dir:
        frame_paths, frame_duration = extract_gif_frames(gif_path, temp_dir, upscale_factor)
        
        # FPS calculation (convert duration in ms to fps)
        fps = 1000 / frame_duration if frame_duration > 0 else 10
        
        # Read frames and create video
        with imageio.get_writer(output_path, fps=fps) as writer:
            for frame_path in frame_paths:
                frame = imageio.imread(frame_path)
                writer.append_data(frame)
                
    print(f"Converted {os.path.basename(gif_path)} to {output_path}")


def process_gifs(input_path, upscale_factor=None, max_workers=None):
    """Process all GIFs in the input path with multithreading"""
    if os.path.isfile(input_path) and input_path.lower().endswith('.gif'):
        output_path = os.path.splitext(input_path)[0] + '.mp4'
        convert_gif_to_video(input_path, output_path, upscale_factor)
        return
    
    if not os.path.isdir(input_path):
        print(f"Error: {input_path} is not a valid file or directory")
        return
    
    # Find all GIF files in the directory
    gif_files = []
    for root, _, files in os.walk(input_path):
        for file in files:
            if file.lower().endswith('.gif'):
                gif_files.append(os.path.join(root, file))
    
    if not gif_files:
        print(f"No GIF files found in {input_path}")
        return
    
    # Process all GIFs using a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for gif_file in gif_files:
            output_path = os.path.splitext(gif_file)[0] + '.mp4'
            future = executor.submit(convert_gif_to_video, gif_file, output_path, upscale_factor)
            futures.append(future)
        
        # Wait for all futures to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error during conversion: {e}")


def main():
    parser = argparse.ArgumentParser(description="Convert GIFs to MP4 videos with optional upscaling")
    parser.add_argument("input", type=str, help="Path to input GIF file or directory containing GIFs")
    parser.add_argument("--upscale", type=int, default=None, 
                        help="Upscale factor (e.g., 2 for 2x upscaling)")
    parser.add_argument("--threads", type=int, default=None,
                        help="Number of parallel threads to use (default: auto)")
    
    args = parser.parse_args()
    
    process_gifs(args.input, args.upscale, args.threads)


if __name__ == "__main__":
    main()
