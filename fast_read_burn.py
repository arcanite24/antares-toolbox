import os
import subprocess
import shutil
import argparse
from lxml import etree, html
from tqdm import tqdm

# Function to apply bold formatting to words based on length
def bold_initial_letters(word):
    length = len(word)
    if length <= 3:
        return f"<strong>{word[0]}</strong>{word[1:]}"
    elif length == 4:
        return f"<strong>{word[:2]}</strong>{word[2:]}"
    else:
        bold_part = word[: max(1, length * 40 // 100)]  # Apply bold to 40% of the word
        return f"<strong>{bold_part}</strong>{word[len(bold_part):]}"


# Function to process HTML content and apply bold transformations
def process_html_content(content):
    # Parse the HTML content
    doc = html.fromstring(content)

    # Process all text nodes within <p> tags (you can extend this to other tags)
    for elem in doc.xpath("//p"):
        if elem.text:
            words = elem.text.split()
            modified_words = [bold_initial_letters(word) for word in words]
            elem.text = " ".join(modified_words)

    # Return the modified HTML content
    return etree.tostring(doc, pretty_print=True, method="html", encoding="unicode")


# Function to extract, modify, and repackage the ebook
def modify_ebook(input_file, output_file, temp_dir="temp_ebook"):
    print(f"Processing '{input_file}'...")

    # Step 1: Extract the content
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    print("Extracting ebook content...")
    extract_command = ["ebook-convert", input_file, os.path.join(temp_dir, "output.epub")]
    subprocess.run(extract_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Step 2: Modify the content
    print("Modifying content...")
    html_files = []
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.endswith(".html") or file.endswith(".xhtml"):
                html_files.append(os.path.join(root, file))

    for file_path in tqdm(html_files, desc="Processing HTML files"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        modified_content = process_html_content(content)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)

    # Step 3: Repackage the modified content back into the desired format
    print("Repackaging modified content...")
    convert_command = [
        "ebook-convert",
        os.path.join(temp_dir, "output.epub"),
        output_file,
    ]
    subprocess.run(convert_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Clean up the temporary directory
    shutil.rmtree(temp_dir)


def main():
    parser = argparse.ArgumentParser(description="Convert ebook to FastRead format")
    parser.add_argument("input_file", help="Input ebook file (EPUB, MOBI, or AZW3)")
    args = parser.parse_args()

    # Use the current working directory as the base for input and output files
    input_file = os.path.abspath(args.input_file)
    file_name, file_extension = os.path.splitext(input_file)
    output_file = f"{file_name}_fastread{file_extension}"

    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    # Check if the input file format is supported
    supported_formats = ['.epub', '.mobi', '.azw3']
    if file_extension.lower() not in supported_formats:
        print(f"Error: Unsupported file format. Please use EPUB, MOBI, or AZW3.")
        return

    modify_ebook(input_file, output_file)
    print(f"Ebook modified and saved as '{output_file}'")

if __name__ == "__main__":
    main()
