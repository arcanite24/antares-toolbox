import os
import argparse
import json
import time
import base64
import requests
from tqdm import tqdm
from dotenv import load_dotenv
import fal_client
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import io

# Load environment variables
load_dotenv()


def sanitize_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in ("-", "_")).rstrip()


def generate_image(
    prompt, image_size, guidance_scale, num_inference_steps, lora_url, lora_scale, seed
):
    try:
        handler = fal_client.submit(
            "fal-ai/flux-lora",
            arguments={
                "prompt": prompt,
                "image_size": image_size,
                "guidance_scale": guidance_scale,
                "num_inference_steps": num_inference_steps,
                "loras": [{"path": lora_url, "scale": lora_scale}],
                "enable_safety_checker": False,
                "seed": seed,
            },
        )
        result = handler.get()
        if "images" in result and result["images"]:
            image_url = result["images"][0]["url"]
            response = requests.get(image_url, timeout=5)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to download image. Status code: {response.status_code}")
                return None
        else:
            print("No images found in the response")
            return None
    except Exception as e:
        print(e)
        return None


def add_prompt_metadata(image_data, prompt):
    img = Image.open(io.BytesIO(image_data))
    metadata = PngInfo()
    metadata.add_text("prompt", prompt)

    # Save the image with metadata to a bytes object
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG", pnginfo=metadata)
    return img_byte_arr.getvalue()


def run_corgi_bench(benchmark_file, lora_url, lora_scale, output_folder, seed, override_image_size=None, override_guidance_scale=None, prefix="", suffix=""):
    with open(benchmark_file, "r") as f:
        benchmark_data = json.load(f)

    prompts = benchmark_data.get("prompts", [])

    if not prompts:
        print("No prompts found in the benchmark file.")
        return

    os.makedirs(output_folder, exist_ok=True)

    for idx, prompt_data in enumerate(tqdm(prompts, desc="Generating images")):
        prompt = prompt_data["prompt"]
        image_size = override_image_size or prompt_data.get("image_size", "square_hd")
        guidance_scale = override_guidance_scale or prompt_data.get("guidance_scale", 3.5)
        num_inference_steps = prompt_data.get("num_inference_steps", 28)

        # Apply prefix and suffix to the prompt
        full_prompt = f"{prefix}{prompt}{suffix}".strip()

        image_data = generate_image(
            full_prompt,
            image_size,
            guidance_scale,
            num_inference_steps,
            lora_url,
            lora_scale,
            seed,
        )

        if image_data:
            image_with_metadata = add_prompt_metadata(image_data, full_prompt)
            output_file = os.path.join(output_folder, f"image_{idx+1}.png")
            with open(output_file, "wb") as f:
                f.write(image_with_metadata)
            print(f"Image saved with metadata: {output_file}")
        else:
            print(f"Failed to generate image for prompt: {prompt}")


def main():
    parser = argparse.ArgumentParser(
        description="CorgiBench - Generate images using FAL Flux-LoRA"
    )
    parser.add_argument(
        "benchmark", help="Name of the benchmark JSON file (without .json extension)"
    )
    parser.add_argument("lora_url", help="URL of the LoRA weights")
    parser.add_argument(
        "--scale", type=float, default=1, help="LoRA scale (default: 1)"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Seed for image generation (default: 42)"
    )
    parser.add_argument(
        "--override_image_size",
        choices=["square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"],
        help="Override the image size for all prompts"
    )
    parser.add_argument(
        "--override_guidance_scale",
        type=float,
        help="Override the guidance scale for all prompts"
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="",
        help="Prefix to add to all prompts"
    )
    parser.add_argument(
        "--suffix",
        type=str,
        default="",
        help="Suffix to add to all prompts"
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    corgi_bench_dir = os.path.join(script_dir, "corgi_bench")
    benchmark_file = os.path.join(corgi_bench_dir, f"{args.benchmark}.json")

    if not os.path.isfile(benchmark_file):
        print(f"Error: Benchmark file '{benchmark_file}' not found.")
        return

    timestamp = int(time.time())
    output_folder = f"corgibench_{sanitize_filename(args.benchmark)}_{timestamp}"

    print(f"Starting CorgiBench with benchmark: {args.benchmark}")
    print(f"LoRA URL: {args.lora_url}")
    print(f"LoRA scale: {args.scale}")
    print(f"Output folder: {output_folder}")

    run_corgi_bench(
        benchmark_file,
        args.lora_url,
        args.scale,
        output_folder,
        args.seed,
        args.override_image_size,
        args.override_guidance_scale,
        args.prefix,
        args.suffix
    )
    print("CorgiBench completed.")


if __name__ == "__main__":
    main()