import os
import argparse
from tqdm import tqdm


def merge_txt_files(input_folder, output_file):
    # Get all .txt files in the input folder
    txt_files = [f for f in os.listdir(input_folder) if f.endswith(".txt")]

    # Open the output file in write mode
    with open(output_file, "w", encoding="utf-8") as outfile:
        # Create a progress bar for file processing
        for filename in tqdm(txt_files, desc="Processing files"):
            file_path = os.path.join(input_folder, filename)

            # Read the content of each file
            with open(file_path, "r", encoding="utf-8") as infile:
                content = infile.read().strip()

            # Write the content to the output file, followed by a newline
            outfile.write(content + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Merge multiple .txt files into a single file."
    )
    parser.add_argument("input_folder", help="Path to the folder containing .txt files")
    parser.add_argument("output_file", help="Path to the output file")

    args = parser.parse_args()

    merge_txt_files(args.input_folder, args.output_file)
    print(f"Merged files saved to {args.output_file}")


if __name__ == "__main__":
    main()
