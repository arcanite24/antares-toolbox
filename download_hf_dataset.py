import argparse
from datasets import load_dataset
import os
import json
import requests
from PIL import Image
from io import BytesIO

def download_image(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        img.save(save_path)
    else:
        print(f"Failed to download image: {url}")

def download_dataset(repo_id, output_folder):
    print(f"Downloading dataset: {repo_id}")
    dataset = load_dataset(repo_id)

    os.makedirs(output_folder, exist_ok=True)

    for split in dataset.keys():
        split_folder = os.path.join(output_folder, split)
        os.makedirs(split_folder, exist_ok=True)

        output_path = os.path.join(split_folder, f"{split}.jsonl")
        print(f"Saving {split} split to: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for idx, item in enumerate(dataset[split]):
                item_copy = item.copy()
                for key, value in item.items():
                    if isinstance(value, dict) and 'bytes' in value:
                        # This is likely an image
                        img_folder = os.path.join(split_folder, 'images')
                        os.makedirs(img_folder, exist_ok=True)
                        img_filename = f"{idx}_{key}.jpg"
                        img_path = os.path.join(img_folder, img_filename)
                        
                        img = Image.open(BytesIO(value['bytes']))
                        img.save(img_path)
                        
                        item_copy[key] = img_filename
                    elif isinstance(value, str) and value.startswith(('http://', 'https://')):
                        # This might be an image URL
                        img_folder = os.path.join(split_folder, 'images')
                        os.makedirs(img_folder, exist_ok=True)
                        img_filename = f"{idx}_{key}.jpg"
                        img_path = os.path.join(img_folder, img_filename)
                        
                        download_image(value, img_path)
                        item_copy[key] = img_filename
                
                json.dump(item_copy, f, ensure_ascii=False)
                f.write('\n')
    
    print("Download complete!")


def main():
    parser = argparse.ArgumentParser(description="Download a Hugging Face dataset")
    parser.add_argument("repo_id", help="The repository ID of the dataset")
    parser.add_argument(
        "--output", default="output", help="The output folder to save the dataset"
    )

    args = parser.parse_args()

    download_dataset(args.repo_id, args.output)


if __name__ == "__main__":
    main()
