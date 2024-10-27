import csv
import json
import os
import shutil


def process(json_folder="jsons", csv_filename="output.csv", reference_file="prompt.json"):
    """
    Convert multiple JSON files in a folder into a single CSV file using a reference file's keys as headers.
    If a JSON file is invalid or has mismatched keys, it is skipped.
    Processed JSON files and their corresponding .txt files are moved to appropriate folders.
    """
    # Load the reference keys from the reference file
    with open(reference_file, "r", encoding="utf-8") as ref_file:
        reference_keys = list(json.load(ref_file).keys())

    processed_folder = "json_processed"
    txt_processed_folder = "txt_processed"
    txts_folder = "txts"

    # Ensure required folders exist
    os.makedirs(processed_folder, exist_ok=True)
    os.makedirs(txt_processed_folder, exist_ok=True)
    os.makedirs(txts_folder, exist_ok=True)

    # Check if the CSV file already exists to determine whether to write headers
    file_exists = os.path.isfile(csv_filename)

    # Open the CSV file in append mode to add new rows without overwriting
    with open(csv_filename, mode="a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=reference_keys)

        # Write the header only if the file is new
        if not file_exists:
            writer.writeheader()

        # Iterate through all JSON files in the folder
        for filename in os.listdir(json_folder):
            if filename.endswith(".json"):
                json_path = os.path.join(json_folder, filename)
                txt_filename = os.path.splitext(filename)[0] + ".txt"
                txt_path_original = os.path.join(txts_folder, txt_filename)
                txt_path_processed = os.path.join(
                    txt_processed_folder, txt_filename)

                # Try loading each JSON file
                try:
                    with open(json_path, "r", encoding="utf-8") as json_file:
                        json_data = json.load(json_file)
                        if not isinstance(json_data, dict):
                            raise ValueError("JSON data is not a dictionary")
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"Skipping invalid JSON file: {filename} ({e})")
                    # Move .txt file back to `txts` folder if it exists
                    if os.path.exists(txt_path_processed):
                        shutil.move(txt_path_processed, txt_path_original)
                    continue

                # Check if JSON keys match reference keys
                if set(json_data.keys()) != set(reference_keys):
                    print(f"Skipping file with mismatched keys: {filename}")
                    # Move .txt file back to `txts` folder if it exists
                    if os.path.exists(txt_path_processed):
                        shutil.move(txt_path_processed, txt_path_original)
                    continue

                # Write the data to the CSV in the correct order
                writer.writerow({key: json_data.get(key, "")
                                for key in reference_keys})

                # Move processed JSON and .txt files
                shutil.move(json_path, os.path.join(
                    processed_folder, filename))
                if os.path.exists(txt_path_original):
                    shutil.move(txt_path_original, txt_path_processed)
                print(f"Processed and moved: {filename}")

    print(f"CSV file '{csv_filename}' updated successfully.")


if __name__ == "__main__":
    process()
