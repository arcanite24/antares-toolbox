import argparse
import os
import pyarrow.parquet as pq
import pandas as pd
from datasets import load_from_disk
from PIL import Image
import io


def extract_parquet(input_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    try:
        # Try loading as a Hugging Face dataset
        dataset = load_from_disk(input_path)
        for i, example in enumerate(dataset):
            if "image" in example:
                img = Image.open(io.BytesIO(example["image"]["bytes"]))
                img.save(os.path.join(output_folder, f"image_{i}.png"))
            else:
                pd.DataFrame([example]).to_csv(
                    os.path.join(output_folder, f"record_{i}.csv"), index=False
                )
        print(f"Extracted Hugging Face dataset to: {output_folder}")
    except:
        # If not a Hugging Face dataset, try as a regular Parquet file
        table = pq.read_table(input_path)
        df = table.to_pandas()

        if "image" in df.columns and df["image"].dtype == "object":
            for i, img_bytes in enumerate(df["image"]):
                img = Image.open(io.BytesIO(img_bytes))
                img.save(os.path.join(output_folder, f"image_{i}.png"))
            print(f"Extracted images to: {output_folder}")
        else:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(output_folder, f"{base_name}.csv")
            df.to_csv(output_path, index=False)
            print(f"Extracted CSV to: {output_path}")


# ... rest of the script (main function) remains the same
