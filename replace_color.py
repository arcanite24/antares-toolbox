import os
import argparse
import concurrent.futures
import numpy as np
from PIL import Image
from tqdm import tqdm

def process_image(image_path, output_path, x, y, new_color):
    """Process a single image with numpy optimization"""
    try:
        # Open and convert image to numpy array
        image = Image.open(image_path)
        img_array = np.array(image)
        
        # Get the color of the pixel at the specified coordinates
        pixel_color = image.getpixel((x, y))
        
        # Create a mask of matching pixels (much faster than iterating)
        if len(img_array.shape) == 3 and img_array.shape[2] >= 3:  # RGB or RGBA
            if len(pixel_color) == 4:  # RGBA
                mask = np.all(img_array == pixel_color, axis=2)
            else:  # RGB
                mask = np.all(img_array[:,:,:len(pixel_color)] == pixel_color, axis=2)
                
            # Apply the new color to masked pixels
            for i in range(min(len(new_color), img_array.shape[2])):
                img_array[:,:,i][mask] = new_color[i]
        else:  # Grayscale
            mask = (img_array == pixel_color)
            img_array[mask] = new_color[0]
            
        # Save the processed image
        result = Image.fromarray(img_array)
        result.save(output_path)
        return f"Processed {os.path.basename(image_path)}"
    except Exception as e:
        return f"Error processing {os.path.basename(image_path)}: {str(e)}"

def replace_color(input_folder, output_folder, x, y, new_color, max_workers=None, batch_size=10):
    """Replace colors in all images using multi-threading"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Collect all valid image files
    image_files = []
    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            image_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            image_files.append((image_path, output_path))
    
    # Process images in parallel batches
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create a list to store futures
        futures = []
        for image_path, output_path in image_files:
            # Submit task to executor
            future = executor.submit(process_image, image_path, output_path, x, y, new_color)
            futures.append(future)
        
        # Process results with progress bar
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing images"):
            print(future.result())

def main():
    parser = argparse.ArgumentParser(description="Replace color in images")
    parser.add_argument(
        "input_folder", help="Path to the input folder containing images"
    )
    parser.add_argument(
        "output_folder", help="Path to the output folder for saving processed images"
    )
    parser.add_argument("x", type=int, help="X-coordinate of the pixel")
    parser.add_argument("y", type=int, help="Y-coordinate of the pixel")
    parser.add_argument(
        "new_color",
        type=str,
        help="New color in the format 'R,G,B' (e.g., '255,0,0' for red)",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=None,
        help="Number of threads to use (default: number of CPU cores)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Batch size for processing images (default: 10)",
    )

    args = parser.parse_args()

    # Parse the new color from the command-line argument
    new_color = tuple(map(int, args.new_color.split(",")))

    replace_color(
        args.input_folder, 
        args.output_folder, 
        args.x, 
        args.y, 
        new_color,
        max_workers=args.threads,
        batch_size=args.batch_size
    )

if __name__ == "__main__":
    main()
