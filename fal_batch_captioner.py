import os
import base64
import sys
from dotenv import load_dotenv
import fal_client

# Load environment variables from .env.local
dotenv_path = os.path.join(os.path.dirname(__file__), ".env.local")
load_dotenv(dotenv_path)

MODEL = "vikhyatk/moondream2"
# PROMPT = """
# describe the subject in good detail, DON'T include anything related to the style or background of the image.

# Start the output by following this template: $SUBJECT
# """

PROMPT = """
Describe this character, don't describe the background or style of the image.
"""

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def process_images_in_folder(folder_path):
    image_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
    images = [
        f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)
    ]

    inputs = []
    image_names = []

    for image_name in images:
        image_path = os.path.join(folder_path, image_name)
        base64_image = encode_image_to_base64(image_path)
        inputs.append(
            {
                "prompt": PROMPT,
                "image_url": f"data:image/png;base64,{base64_image}",
            }
        )
        image_names.append(image_name)

    if inputs:
        handler = fal_client.submit(
            "fal-ai/moondream/batched",
            arguments={
                "inputs": inputs,
                "model_id": MODEL,
            },
        )

        results = handler.get()["outputs"]

        for image_name, output_string in zip(image_names, results):
            output_file_path = os.path.join(
                folder_path, f"{os.path.splitext(image_name)[0]}.txt"
            )
            with open(output_file_path, "w") as output_file:
                output_file.write(output_string)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <target_folder>")
        sys.exit(1)

    target_folder = sys.argv[1]
    if not os.path.isdir(target_folder):
        print(f"Error: {target_folder} is not a valid directory.")
        sys.exit(1)

    process_images_in_folder(target_folder)
