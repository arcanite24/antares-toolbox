import os
import argparse
from tqdm import tqdm


def fix_file_encoding(file_path):
    try:
        # Try to read the file with 'utf-8' encoding first
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except UnicodeDecodeError:
        # If 'utf-8' fails, try 'latin-1' (which can read all byte sequences)
        with open(file_path, "r", encoding="latin-1") as file:
            content = file.read()

    # Write the content back to the file using UTF-8 encoding
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def process_folder(input_folder):
    txt_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".txt")]

    for filename in tqdm(txt_files, desc="Processing files"):
        file_path = os.path.join(input_folder, filename)
        fix_file_encoding(file_path)
        print(f"Fixed encoding for {filename}")


def main():
    parser = argparse.ArgumentParser(description="Fix encoding issues in .txt files")
    parser.add_argument(
        "input_folder", type=str, help="Folder containing .txt files to fix"
    )
    args = parser.parse_args()

    process_folder(args.input_folder)
    print("Encoding fix completed for all .txt files in the folder.")


if __name__ == "__main__":
    main()
