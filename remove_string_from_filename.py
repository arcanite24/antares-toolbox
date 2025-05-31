import os
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


def process_file(file_path, match_string, replacement):
    directory, filename = os.path.split(file_path)
    new_filename = filename.replace(match_string, replacement)
    new_file_path = os.path.join(directory, new_filename)

    if filename != new_filename:
        os.rename(file_path, new_file_path)
    return new_file_path


def process_directory(directory, match_string, replacement):
    files_to_process = []
    for root, _, files in os.walk(directory):
        for file in files:
            files_to_process.append(os.path.join(root, file))

    with ThreadPoolExecutor() as executor:
        list(
            tqdm(
                executor.map(
                    lambda f: process_file(f, match_string, replacement),
                    files_to_process,
                ),
                total=len(files_to_process),
                desc="Processing files",
            )
        )


def main():
    parser = argparse.ArgumentParser(description="Remove a string from filenames")
    parser.add_argument("input", help="Input file or directory")
    parser.add_argument("match_string", help="String to match in filenames")
    parser.add_argument(
        "replacement", help="Replacement string (use empty quotes for removal)"
    )
    args = parser.parse_args()

    if os.path.isfile(args.input):
        new_file_path = process_file(args.input, args.match_string, args.replacement)
        print(f"Processed file: {new_file_path}")
    elif os.path.isdir(args.input):
        process_directory(args.input, args.match_string, args.replacement)
        print("Finished processing directory")
    else:
        print(f"Error: {args.input} is not a valid file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
