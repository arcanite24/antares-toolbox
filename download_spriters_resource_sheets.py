import os
import requests
from bs4 import BeautifulSoup
import argparse
import logging
from urllib.parse import urlparse, urljoin
from tqdm import tqdm
import re
import zipfile

def download_image(url, output_folder):
    response = requests.get(url)
    if response.status_code == 200:
        parsed_url = urlparse(url)
        filename = os.path.join(output_folder, os.path.basename(parsed_url.path))
        with open(filename, "wb") as file:
            file.write(response.content)
        logging.info(f"Downloaded: {filename}")
    else:
        logging.warning(f"Failed to download: {url}")


def sanitize_filename(filename):
    # Remove invalid characters and trim quotes/semicolons
    filename = filename.strip('";')
    # Replace invalid Windows filename characters
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, "_", filename)


def scrape_images(base_url, url, output_folder, download_zips=False):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        update_sheet_icons = soup.find_all(class_="updatesheeticons")
        total_icons = len(update_sheet_icons)
        logging.info(f"Found {total_icons} update sheet icons")

        for icon in tqdm(update_sheet_icons, desc="Processing icons", unit="icon"):
            links = icon.find_all("a")
            total_links = len(links)
            logging.info(f"Found {total_links} links for the current icon")

            for link in links:
                href = link.get("href")
                if href:
                    sheet_url = base_url + href
                    sheet_response = requests.get(sheet_url)
                    if sheet_response.status_code == 200:
                        sheet_soup = BeautifulSoup(sheet_response.text, "html.parser")

                        if download_zips:
                            sheet_container = sheet_soup.find(id="content")
                        else:
                            sheet_container = sheet_soup.find(id="sheet-container")

                        if download_zips and sheet_container:
                            download_links = sheet_container.find_all("a", href=re.compile(r"/download/\d+"))
                            total_links = len(download_links)
                            logging.info(f"Found {total_links} download links in the content")

                            for dl_link in tqdm(download_links, desc="Processing downloads", unit="file", leave=False):
                                download_url = urljoin(base_url, dl_link["href"])
                                try:
                                    response = requests.get(download_url, stream=True)
                                    response.raise_for_status()

                                    # Extract filename from Content-Disposition header
                                    content_disposition = response.headers.get('content-disposition', '')
                                    if 'filename=' in content_disposition:
                                        filename = content_disposition.split('filename=')[-1]
                                        filename = sanitize_filename(filename)
                                    else:
                                        # Fallback filename based on URL
                                        filename = f"sheet_{dl_link['href'].split('/')[-1]}.zip"
                                    
                                    filepath = os.path.join(output_folder, filename)
                                    
                                    with open(filepath, 'wb') as f:
                                        for chunk in response.iter_content(chunk_size=8192):
                                            f.write(chunk)

                                    # If it's a zip file, extract it
                                    if filename.lower().endswith('.zip'):
                                        with zipfile.ZipFile(filepath) as zf:
                                            extract_path = os.path.join(output_folder, 'sheets')
                                            zf.extractall(extract_path)
                                        # Optionally remove the zip file after extraction
                                        os.remove(filepath)
                                        logging.info(f"Extracted {filename} to {extract_path}")
                                    else:
                                        logging.info(f"Downloaded {filename}")

                                except requests.exceptions.RequestException as e:
                                    logging.error(f"Failed to download {download_url}: {e}")
                                except zipfile.BadZipFile:
                                    logging.error(f"Invalid zip file: {filepath}")
                                    if os.path.exists(filepath):
                                        os.remove(filepath)
                        else:
                            if sheet_container:
                                images = sheet_container.find_all("img")
                                total_images = len(images)
                                logging.info(
                                    f"Found {total_images} images in the sheet container"
                                )

                                for image in tqdm(
                                    images,
                                    desc="Downloading images",
                                    unit="image",
                                    leave=False,
                                ):
                                    image_url = base_url + image["src"]
                                    download_image(image_url, output_folder)
                            else:
                                logging.warning(f"Sheet container not found: {sheet_url}")
                    else:
                        logging.warning(f"Failed to load sheet: {sheet_url}")
    else:
        logging.error(f"Failed to load URL: {url}")


def main():
    parser = argparse.ArgumentParser(description="Image Scraper")
    parser.add_argument(
        "-u", "--url", type=str, required=True, help="URL to scrape images from"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Output folder for downloaded images",
    )
    parser.add_argument(
        "-z",
        "--download-zips",
        action="store_true",
        help="Download and extract zip files from /download/ links",
    )
    args = parser.parse_args()

    base_url = "https://www.spriters-resource.com"
    url = args.url
    output_folder = args.output

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        filename=os.path.join(output_folder, "log.txt"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    logging.info(f"Starting image scraping from: {url}")
    scrape_images(base_url, url, output_folder, args.download_zips)
    logging.info("Image scraping completed")


if __name__ == "__main__":
    main()
