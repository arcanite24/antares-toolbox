import argparse
import os

def replace_string_in_file(file_path, search_string, replace_string):
    # Open and read the file
    with open(file_path, 'r', encoding='utf-8') as file:
        filedata = file.read()
    
    # Replace the target string
    filedata = filedata.replace(search_string, replace_string)
    
    # Write the file out again
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(filedata)

def replace_in_txt_files(folder_path, search_string, replace_string):
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            replace_string_in_file(file_path, search_string, replace_string)
            print(f"Replaced in {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replace a string in all .txt files within a specified directory.")
    parser.add_argument("folder_path", type=str, help="The path to the directory containing .txt files")
    parser.add_argument("search_string", type=str, help="The string to search for")
    parser.add_argument("replace_string", type=str, help="The string to replace the search string with")
    
    args = parser.parse_args()
    
    replace_in_txt_files(args.folder_path, args.search_string, args.replace_string)
