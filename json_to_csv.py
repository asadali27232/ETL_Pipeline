import csv
import json
import os
import shutil
import pandas as pd
from collections import OrderedDict


def process(json_folder="jsons", csv_filename="output.csv", reference_file="prompt.json"):
    """
    Convert multiple JSON files in a folder into a single CSV file using a reference file's keys as headers.
    Only files with matching keys will be processed, and processed files are moved to an existing `json_processed` folder.
    If a JSON file is invalid or has mismatched keys, it is skipped, and the corresponding .txt file is moved back to `txts` folder.

    :param json_folder: Path to the folder containing JSON files.
    :param csv_filename: Name of the output CSV file.
    :param reference_file: Path to the reference JSON file with the correct set of keys.
    """
    # Load the reference keys from prompt.json in order
    with open(reference_file, "r", encoding="utf-8") as ref_file:
        reference_data = json.load(ref_file)
        reference_keys = list(reference_data.keys())

    processed_folder = "json_processed"
    txt_processed_folder = "txt_processed"
    txts_folder = "txts"

    # Ensure required folders exist
    os.makedirs(json_folder, exist_ok=True)
    os.makedirs(processed_folder, exist_ok=True)
    os.makedirs(txt_processed_folder, exist_ok=True)
    os.makedirs(txts_folder, exist_ok=True)

    # Prepare a set for existing entries to avoid duplicates
    existing_data = set()

    # Check if the CSV file already exists and load existing entries
    if os.path.exists(csv_filename):
        with open(csv_filename, mode='r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip header
            # Assumes the first column is the unique identifier
            existing_data.update(row[0] for row in reader)

    # Open a temporary CSV file to write data for the current run
    temp_csv_filename = "temp_output.csv"
    with open(temp_csv_filename, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=reference_keys)
        writer.writeheader()

        # Iterate through all JSON files in the folder
        for filename in os.listdir(json_folder):
            if filename.endswith(".json"):
                json_path = os.path.join(json_folder, filename)
                txt_filename = os.path.splitext(filename)[0] + ".txt"
                txt_path_processed = os.path.join(
                    txt_processed_folder, txt_filename)
                txt_path_original = os.path.join(txts_folder, txt_filename)

                # Try loading each JSON file
                try:
                    with open(json_path, "r", encoding="utf-8") as json_file:
                        json_data = json.load(json_file)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON file: {filename}")

                    # Move corresponding .txt file back to `txts` folder if it exists
                    if os.path.exists(txt_path_processed):
                        shutil.move(txt_path_processed, txt_path_original)
                        print(f"Moved '{txt_filename}' back to 'txts' folder.")
                    continue

                # Check if JSON keys match reference keys
                file_keys = set(json_data.keys())
                if file_keys != set(reference_keys):
                    print(f"Skipping file with mismatched keys: {filename}")

                    # Move corresponding .txt file back to `txts` folder if it exists
                    if os.path.exists(txt_path_processed):
                        shutil.move(txt_path_processed, txt_path_original)
                        print(f"Moved '{txt_filename}' back to 'txts' folder.")
                    continue

                # Reorder json_data according to reference_keys and wrap values in quotes
                ordered_data = OrderedDict(
                    (key, f'"{json_data.get(key, "")}"') for key in reference_keys)

                # Check if this entry is already in existing data
                # Assumes first key is the unique identifier
                unique_identifier = ordered_data[reference_keys[0]]
                if unique_identifier in existing_data:
                    print(f"Skipping duplicate entry for: {unique_identifier}")
                    continue

                # Write each JSON dictionary as a row in the temporary CSV file
                writer.writerow(ordered_data)
                print(f"Processed and added '{filename}' to temporary CSV.")

                # Move processed file to the json_processed folder
                try:
                    shutil.move(json_path, os.path.join(
                        processed_folder, filename))
                    print(f"Moved '{filename}' to '{processed_folder}'.")
                except PermissionError as e:
                    print(f"PermissionError: {
                          e} - Could not move {filename}. It may be open in another program.")
                except FileNotFoundError as e:
                    print(f"FileNotFoundError: {
                          e} - Could not find destination path.")

    # If the temporary CSV has data, append it to the existing output CSV
    if os.path.exists(temp_csv_filename):
        temp_df = pd.read_csv(temp_csv_filename)
        temp_df.to_csv(csv_filename, mode='a', header=False,
                       index=False)  # Append without header

    # Remove the temporary CSV file
    os.remove(temp_csv_filename)

    print(f"CSV file '{csv_filename}' updated successfully.")


if __name__ == "__main__":
    process("jsons", "output.csv")
