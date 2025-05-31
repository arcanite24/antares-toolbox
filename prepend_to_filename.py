import os
import sys


def prepend_string_to_filenames(folder_path, prepend_string):
    """
    Prepends a string to all filenames in the specified folder.
    
    Args:
        folder_path (str): Path to the folder containing files to rename
        prepend_string (str): String to prepend to each filename
    """
    files = os.listdir(folder_path)
    
    for filename in files:
        # Skip directories
        if os.path.isdir(os.path.join(folder_path, filename)):
            continue
            
        # Create new filename with prepended string
        new_filename = prepend_string + filename
        
        # Create full paths for old and new filenames
        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(folder_path, new_filename)
        
        # Rename the file
        os.rename(old_path, new_path)
        print(f"Renamed: {filename} -> {new_filename}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python prepend_filename.py <target_folder> <string_to_prepend>")
        sys.exit(1)

    target_folder = sys.argv[1]
    string_to_prepend = sys.argv[2]

    if not os.path.isdir(target_folder):
        print(f"Error: {target_folder} is not a valid directory.")
        sys.exit(1)

    prepend_string_to_filenames(target_folder, string_to_prepend)
    print(f"Successfully prepended '{string_to_prepend}' to filenames in {target_folder}")