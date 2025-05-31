import argparse
from tqdm import tqdm


def deduplicate_lines(input_file, output_file):
    unique_lines = set()
    total_lines = 0
    unique_count = 0

    # Count total lines for the progress bar
    with open(input_file, "r", encoding="utf-8") as f:
        total_lines = sum(1 for _ in f)

    with open(input_file, "r", encoding="utf-8") as infile, open(
        output_file, "w", encoding="utf-8"
    ) as outfile:

        for line in tqdm(infile, total=total_lines, desc="Deduplicating lines"):
            line = line.strip()
            if line not in unique_lines:
                unique_lines.add(line)
                outfile.write(line + "\n")
                unique_count += 1

    print(f"Total lines: {total_lines}")
    print(f"Unique lines: {unique_count}")
    print(f"Removed {total_lines - unique_count} duplicate lines")


def main():
    parser = argparse.ArgumentParser(description="Deduplicate lines in a text file.")
    parser.add_argument("input_file", help="Path to the input text file")
    parser.add_argument("-o", "--output", help="Path to the output file (optional)")

    args = parser.parse_args()

    if args.output:
        output_file = args.output
    else:
        output_file = args.input_file.rsplit(".", 1)[0] + "_dedup.txt"

    deduplicate_lines(args.input_file, output_file)
    print(f"Deduplicated file saved to {output_file}")


if __name__ == "__main__":
    main()
