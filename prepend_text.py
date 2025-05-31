import os
import sys


def prepend_string_to_txt_files(folder_path, prepend_string):
    txt_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".txt")]

    for txt_file in txt_files:
        file_path = os.path.join(folder_path, txt_file)

        with open(file_path, "r") as file:
            content = file.read()

        with open(file_path, "w") as file:
            file.write(prepend_string + content)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <target_folder> <string_to_prepend>")
        sys.exit(1)

    target_folder = sys.argv[1]
    string_to_prepend = sys.argv[2]

    if not os.path.isdir(target_folder):
        print(f"Error: {target_folder} is not a valid directory.")
        sys.exit(1)

    prepend_string_to_txt_files(target_folder, string_to_prepend)
