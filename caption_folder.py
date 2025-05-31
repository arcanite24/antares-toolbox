import os
import argparse
import base64
from antares import Antares
from tqdm import tqdm
import concurrent.futures

antares = Antares()
client = antares.openrouter

DEFAULT_SYSTEM_PROMPT = """
    You are a system in charge of creating descriptions/captions for $TASK.
    $EXTRA_INSTRUCTIONS
    
    $EXAMPLES
    
    Output only the description, nothing else.
    Don't start the description with things like 'This image depicts' or 'This image shows'.
"""


def describe_image(img_path, prompt, model):
    try:
        with open(img_path, "rb") as img_file:
            img_data = img_file.read()
            base64_image = base64.b64encode(img_data).decode("utf-8")

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                            }
                        ],
                    },
                ],
                max_tokens=1024,
            )

            return response.choices[0].message.content
    except Exception as e:
        print(f"Error processing image {img_path}: {e}")
        return None


def process_single_image(img_data):
    """Process a single image with the given parameters"""
    img_path, prompt, model, output_format = img_data
    filename = os.path.basename(img_path)
    caption = describe_image(img_path, prompt, model)
    output_path = os.path.splitext(img_path)[0] + f".{output_format}"
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(caption)
    return filename, output_path


def process_images(input_folder, output_format, prompt, model, test_mode=False, num_threads=4):
    image_files = [
        f
        for f in os.listdir(input_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"))
    ]

    if test_mode:
        image_files = image_files[:1]  # Process only the first image in test mode

    # Prepare the arguments for each image
    img_data = [
        (os.path.join(input_folder, filename), prompt, model, output_format)
        for filename in image_files
    ]

    # Use ThreadPoolExecutor to process images in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(tqdm(
            executor.map(process_single_image, img_data),
            total=len(img_data),
            desc="Processing images"
        ))
    
    for filename, output_path in results:
        print(f"Caption for {filename} saved to {output_path}")


def read_prompt_file(file_path):
    with open(file_path, "r") as file:
        return file.read().strip()


def main():
    parser = argparse.ArgumentParser(description="Caption images using GPT-4o")
    parser.add_argument(
        "input_folder", type=str, help="Folder containing images to caption"
    )
    parser.add_argument(
        "--output_format",
        type=str,
        default="txt",
        help="Output format for captions (default: txt)",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        help="Custom system prompt to use for generating descriptions",
    )
    parser.add_argument(
        "--task",
        type=str,
        help="Task to replace $TASK in the system prompt. Useful when using the default prompt. Add something like 'pixel art images', 'swords', 'fantasy art', etc.",
        default="images",
    )
    parser.add_argument(
        "--extra",
        type=str,
        help="Extra instructions to replace $EXTRA_INSTRUCTIONS in the system prompt.",
        default="",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="google/gemini-2.5-flash-preview",
        help="Model to use for generating descriptions (default: google/gemini-2.5-flash-preview)",
    )
    parser.add_argument(
        "--examples",
        type=str,
        default="""
        Follow this examples:
        - A cute corgi wearing sunglasses and a cool party hat, pastel color background
        - A wizard with a wand, in a medieval setting, with a starry sky background
        - A futuristic cityscape with flying cars and neon lights
        - A big sword with a wooden handle, sharp and shiny blade with a red gem
        """,
        help="Examples to replace $EXAMPLES in the system prompt.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode: only caption the first image in the folder",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=10,
        help="Number of threads to use for parallel processing (default: 10)",
    )
    args = parser.parse_args()

    global DEFAULT_SYSTEM_PROMPT
    prompt = DEFAULT_SYSTEM_PROMPT
    if args.prompt:
        if args.prompt.endswith(".txt"):
            prompt = read_prompt_file(args.prompt)
        else:
            prompt = args.prompt

    if not args.prompt:
        if args.task:
            prompt = prompt.replace("$TASK", args.task)
        if args.extra:
            prompt = prompt.replace("$EXTRA_INSTRUCTIONS", args.extra)
        if args.examples:
            prompt = prompt.replace("$EXAMPLES", args.examples)


    print(f"Using model: {args.model}")

    process_images(
        args.input_folder, args.output_format, prompt, args.model, args.test,
        num_threads=args.threads
    )


if __name__ == "__main__":
    main()
