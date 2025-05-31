import argparse
from safetensors import safe_open


def list_keys(filepath):
    try:
        with safe_open(filepath, framework="pt") as f:
            keys = f.keys()
            print("Keys in the .safetensors file:")
            for key in keys:
                print(key)
    except Exception as e:
        print(f"Error reading the file: {e}")


def main():
    parser = argparse.ArgumentParser(description="List all keys in a .safetensors file")
    parser.add_argument("filepath", type=str, help="Path to the .safetensors file")
    args = parser.parse_args()

    list_keys(args.filepath)


if __name__ == "__main__":
    main()
