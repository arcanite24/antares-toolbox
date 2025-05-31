import argparse
import json
import logging
import os
import re
import time

from comfy_api_simplified import ComfyApiWrapper, ComfyWorkflowWrapper
from tqdm import tqdm


def setup_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def sanitize_filename(filename):
    return re.sub(r"[^\w\-_\. ]", "_", filename).replace(" ", "_")


def main(workflow_file, prompts_file, output_folder, batch_size, output_node):
    setup_logging()
    logging.info(f"Starting execution with workflow: {workflow_file}")

    api = ComfyApiWrapper("http://127.0.0.1:8188/")
    wf = ComfyWorkflowWrapper(workflow_file)

    with open(prompts_file, "r") as f:
        prompts_data = json.load(f)
        prompts = prompts_data.get("prompts", [])

    if not prompts:
        logging.error("No prompts found in the JSON file")
        return

    os.makedirs(output_folder, exist_ok=True)

    for prompt in tqdm(prompts, desc="Processing prompts"):
        start_time = time.time()

        wf.set_node_param("Positive", "text", prompt)
        wf.set_node_param("Empty Latent Image", "batch_size", batch_size)

        logging.info(f"Queuing workflow for prompt: {prompt}")
        results = api.queue_and_wait_images(wf, output_node)

        elapsed_time = int(time.time() - start_time)
        base_filename = sanitize_filename(prompt)

        for i, (_, image_data) in enumerate(results.items()):
            output_filename = f"{base_filename}_{elapsed_time}s_{i}.png"
            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, "wb+") as f:
                f.write(image_data)

            logging.info(f"Saved image: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ComfyUI Workflow Executor")
    parser.add_argument("workflow_file", help="Path to the workflow JSON file")
    parser.add_argument("prompts_file", help="Path to the JSON file containing prompts")
    parser.add_argument(
        "output_folder", help="Path to the output folder for generated images"
    )
    parser.add_argument(
        "--batch_size", type=int, default=1, help="Batch size for image generation"
    )
    parser.add_argument(
        "--output_node", default="Quantized Output", help="Name of the output node"
    )

    args = parser.parse_args()

    main(
        args.workflow_file,
        args.prompts_file,
        args.output_folder,
        args.batch_size,
        args.output_node,
    )
