import os
import argparse
import logging
import concurrent.futures
import requests
from bs4 import BeautifulSoup
from PIL import Image
from tqdm import tqdm
from urllib.parse import urlparse

BASE_URL = "https://www.spriters-resource.com"

def download_image(url, output_folder):
    url = BASE_URL + url
    
    response = requests.get(url)
    if response.status_code == 200:
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        file_path = os.path.join(output_folder, filename)
        with open(file_path, "wb") as file:
            file.write(response.content)
        try:
            img = Image.open(file_path)
            img.save(
                file_path, format=img.format, transparency=img.info.get("transparency")
            )
        except Exception as e:
            logging.error(f"Error processing image {file_path}: {str(e)}")
        return file_path
    else:
        logging.error(f"Failed to download image from URL: {url}")
        return None


def download_images(url, output_folder, max_workers=None):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        img_elements = soup.select(".iconcontainer > .iconbody > img")
        img_urls = [img["src"] for img in img_elements]

        os.makedirs(output_folder, exist_ok=True)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(download_image, img_url, output_folder)
                for img_url in img_urls
            ]
            with tqdm(total=len(futures), unit="image") as pbar:
                for future in concurrent.futures.as_completed(futures):
                    file_path = future.result()
                    if file_path:
                        logging.info(f"Downloaded image: {file_path}")
                    pbar.update(1)
    else:
        logging.error(
            f"Failed to fetch the webpage. Status code: {response.status_code}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download images from a webpage.")
    parser.add_argument("url", type=str, help="URL of the webpage")
    parser.add_argument(
        "output_folder", type=str, help="Output folder for downloaded images"
    )
    parser.add_argument(
        "--max-workers", type=int, default=None, help="Maximum number of worker threads"
    )
    parser.add_argument(
        "--log-level", type=str, default="INFO", help="Logging level (default: INFO)"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=args.log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    download_images(args.url, args.output_folder, args.max_workers)
