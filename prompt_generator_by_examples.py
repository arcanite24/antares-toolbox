from antares import Antares
import argparse
import time
import json
from typing import List
from tqdm import tqdm
import logging
import os
import re

antares = Antares()
client = antares.groq

BASE_PROMPT = """
We need to generate a list of prompts for a text-to-image model based on the provided examples and theme.
Adhere to the following guidelines:
- Don't write them as instructions, but as prompts or descriptions.
- The prompts should be relevant to the theme.
- The prompts should be inspired by the provided examples.
- You will answer with a JSON array of prompts and only THAT!
- Follow the examples closely and make sure you generate prompts that are similar in style.
- You should generate $AMOUNT prompts.
- Don't answer with Markdown, just the JSON object with the array of prompts.

The theme is: $THEME

The examples are:
$EXAMPLES

You need to answer in the following JSON format:
{
    "prompts": [
        "prompt 1",
        "prompt 2",
        "prompt 3",
        ...
    ]
}
"""


def is_valid_json(json_string):
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False


def generate_prompts(theme, examples, model, amount, max_retries=3, wait_time=2):
    process_prompt = (
        BASE_PROMPT.replace("$THEME", theme)
        .replace("$EXAMPLES", examples)
        .replace("$AMOUNT", str(amount))
    )

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": process_prompt}],
            )
            content = response.choices[0].message.content

            if is_valid_json(content):
                return content
            else:
                print(content)
                print(f"Attempt {attempt + 1}: Invalid JSON response. Retrying...")
        except Exception as e:
            print(f"Attempt {attempt + 1}: Error occurred: {str(e)}. Retrying...")

        if attempt < max_retries - 1:
            time.sleep(wait_time)  # Wait for the specified time before retrying

    raise Exception(f"Failed to generate valid prompts after {max_retries} attempts.")


def read_text_files(input_path: str) -> str:
    all_text = []
    if os.path.isfile(input_path):
        with open(input_path, "r", encoding="utf-8") as f:
            all_text.append(f.read())
    elif os.path.isdir(input_path):
        for filename in os.listdir(input_path):
            if filename.endswith(".txt"):
                with open(
                    os.path.join(input_path, filename), "r", encoding="utf-8"
                ) as f:
                    all_text.append(f.read())
    else:
        raise ValueError(f"Invalid input path: {input_path}")
    return "\n".join(all_text)


def generate_multiple_prompts(
    theme: str,
    examples: str,
    model: str,
    amount: int,
    repeats: int,
    max_retries: int = 3,
    wait_time: float = 2.0,
) -> List[str]:
    all_prompts = []
    for _ in tqdm(range(repeats), desc="Generating prompts", unit="batch"):
        prompts_json = generate_prompts(theme, examples, model, amount, max_retries, wait_time)
        prompts = json.loads(prompts_json)["prompts"]
        all_prompts.extend(prompts)
        time.sleep(wait_time)  # Wait between batches
    return all_prompts


def sanitize_filename(filename):
    # Remove invalid characters and replace spaces with underscores
    return re.sub(r"[^\w\-_\. ]", "", filename).replace(" ", "_")


def main():
    parser = argparse.ArgumentParser(
        description="Generate prompts based on examples and a theme."
    )
    parser.add_argument(
        "input_path", help="Path to a .txt file or a folder containing .txt files"
    )
    parser.add_argument("theme", help="Theme for prompt generation")
    parser.add_argument(
        "--output",
        help="Path to the output JSON file",
    )
    parser.add_argument(
        "--model",
        default="llama-3.1-70b-versatile",
        help="Model to use for generation",
    )
    parser.add_argument(
        "--max_retries", type=int, default=3, help="Maximum number of retries"
    )
    parser.add_argument(
        "--repeats", type=int, default=3, help="Number of times to generate prompts"
    )
    parser.add_argument(
        "--amount", type=int, default=10, help="Number of prompts to generate per batch"
    )
    parser.add_argument(
        "--wait_time",
        type=float,
        default=2.0,
        help="Wait time in seconds between requests (default: 2.0)",
    )

    args = parser.parse_args()

    if not args.output:
        sanitized_theme = sanitize_filename(args.theme)
        args.output = f"{sanitized_theme}_prompts.json"

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    examples = read_text_files(args.input_path)

    logging.info("Initial Information:")
    logging.info(f"Theme: {args.theme}")
    logging.info(f"Model: {args.model}")
    logging.info(f"Input path: {args.input_path}")
    logging.info(
        f"Output file: {args.output}"
    )  # Changed from args.output_file to args.output
    logging.info(f"Max retries: {args.max_retries}")
    logging.info(f"Repeats: {args.repeats}")
    logging.info(f"Number of characters in examples: {len(examples)}")
    logging.info(f"Wait time between requests: {args.wait_time} seconds")

    try:
        all_prompts = generate_multiple_prompts(
            args.theme,
            examples,
            args.model,
            args.amount,
            args.repeats,
            args.max_retries,
            args.wait_time,
        )

        output = {"prompts": all_prompts}

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        logging.info(f"Prompts generated and saved to {args.output}")
        logging.info(f"Total prompts generated: {len(all_prompts)}")
    except Exception as e:
        logging.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
