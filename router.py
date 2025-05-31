#!/usr/bin/env python3

import sys
import subprocess
import os


def main():
    if len(sys.argv) < 2:
        print("Usage: router.py <script_name> [<args>...]")
        sys.exit(1)

    script_name = sys.argv[1]
    script_args = sys.argv[2:]

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(script_dir, f"{script_name}.py")

    if not os.path.isfile(script_path):
        print(f"Unknown script: {script_name}")
        sys.exit(1)

    subprocess.run([sys.executable, script_path] + script_args)


if __name__ == "__main__":
    main()
