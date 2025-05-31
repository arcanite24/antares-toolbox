from antares import Antares
import argparse
import time
import json
from typing import List
from tqdm import tqdm
import logging

antares = Antares()
client = antares.cerebras

BASE_PROMPT = """
We need to generate a list of prompts for a text-to-image model given a theme and a list of examples.
Adhere to the following guidelines:
- Don't write them as instructions, but as prompts or descriptions.
- The prompts should be concise and to the point.
- The prompts should be relevant to the theme.
- The prompts should be specific to the examples.
- You will answer with a JSON array of prompts and only THAT!.
- Follow the examples closely and make sure you generate prompts that are similar to the examples.
- If the examples start with something realted to the type of the image, make sure to include that in the prompts.
- You should genetate $AMOUNT prompts.
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


def generate_prompts(theme, examples, model, amount, max_retries=3):
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
            time.sleep(1)  # Wait for 1 second before retrying

    raise Exception(f"Failed to generate valid prompts after {max_retries} attempts.")


def generate_multiple_prompts(
    theme: str,
    examples: str,
    model: str,
    amount: int,
    repeats: int,
    max_retries: int = 3,
) -> List[str]:
    all_prompts = []
    for _ in tqdm(range(repeats), desc="Generating prompts", unit="batch"):
        prompts_json = generate_prompts(theme, examples, model, amount, max_retries)
        prompts = json.loads(prompts_json)["prompts"]
        all_prompts.extend(prompts)
    return all_prompts


import os

def main():
    parser = argparse.ArgumentParser(
        description="Generate prompts based on a theme and examples."
    )
    parser.add_argument(
        "examples_file", help="Path to the .txt file containing examples"
    )
    parser.add_argument("theme", help="Theme for prompt generation")
    parser.add_argument(
        "output_file",
        nargs="?",
        default="prompts.json",
        help="Path to the output JSON file",
    )
    parser.add_argument(
        "--model",
        default="llama3.1-70b",
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

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Get the current working directory (where the script is executed)
    cwd = os.getcwd()

    # Handle relative paths correctly
    examples_file = os.path.abspath(args.examples_file)
    output_file = os.path.abspath(args.output_file)

    logging.info("Initial Information:")
    logging.info(f"Current working directory: {cwd}")
    logging.info(f"Theme: {args.theme}")
    logging.info(f"Model: {args.model}")
    logging.info(f"Examples file: {examples_file}")
    logging.info(f"Output file: {output_file}")
    logging.info(f"Max retries: {args.max_retries}")
    logging.info(f"Repeats: {args.repeats}")

    try:
        with open(examples_file, "r") as f:
            examples = f.read()

        logging.info(f"Number of examples loaded: {len(examples.splitlines())}")

        all_prompts = generate_multiple_prompts(
            args.theme, examples, args.model, args.amount, args.repeats, args.max_retries
        )

        output = {"prompts": all_prompts}

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        logging.info(f"Prompts generated and saved to {output_file}")
        logging.info(f"Total prompts generated: {len(all_prompts)}")
    except Exception as e:
        logging.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
