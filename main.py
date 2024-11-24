import re
import os
import json
import shutil
import txt_to_json
import json_to_csv
import append
import finalizer


# Define directories
txt_dir = 'txts/'
json_dir = 'jsons/'
processed_txt_dir = 'txt_processed/'
json_processed_dir = 'json_processed/'

csv_filename = 'University'
append_filename = 'append.txt'


confirmation = input(
    "Are you sure you have written Extra Append Information (append.txt) in append.txt file? (y/n): ")
if confirmation.lower() != 'y':
    print("Please write Extra Append Information in append.txt file and run the program again.")
    exit()


# Get and clean the CSV filename from the user in one line
csv_filename = re.sub(r'[^a-zA-Z0-9 ]', '', str(input(
    "Enter the name of the current University): ")).strip())

csv_filename = csv_filename + ' Courses.csv'

append.append_to_txts()

print(f"CSV filename set to: {csv_filename}")

# Create directories if they don't exist
os.makedirs(json_dir, exist_ok=True)
os.makedirs(processed_txt_dir, exist_ok=True)
os.makedirs(txt_dir, exist_ok=True)
os.makedirs(json_processed_dir, exist_ok=True)


def process_text_files():
    # Open error log file
    # Loop through each text file in the directory
    for filename in os.listdir(txt_dir):
        if filename.endswith('.txt'):
            txt_path = os.path.join(txt_dir, filename)
            json_filename = os.path.splitext(filename)[0] + '.json'
            json_path = os.path.join(json_dir, json_filename)

            try:
                # Read the content from the text file
                with open(txt_path, 'r', encoding="utf-8") as file:
                    contents = file.read()

                try:
                    # Summarize the text
                    summary = txt_to_json.summarize_text(contents)

                    try:
                        # Ensure summary is in JSON format
                        summary_json = json.loads(summary)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON for {
                            filename}. Saving raw summary.\n")
                        summary_json = summary  # Use raw summary if JSON decoding fails

                    # Save the summary to a JSON file
                    with open(json_path, 'w', encoding='utf-8') as file:
                        json.dump(summary_json, file,
                                  ensure_ascii=False, indent=4)

                    print(f"Summarized {filename} and saved summary to {
                          json_filename}")

                    # Move processed text file to the processed folder
                    shutil.move(txt_path, os.path.join(
                        processed_txt_dir, filename))

                except Exception as e:
                    error_message = f"Error summarizing {filename}: {e}\n"
                    print(error_message)

            except Exception as e:
                error_message = f"Error reading {filename}: {e}\n"
                print(error_message)


def process_json_files():
    try:
        json_to_csv.process(json_dir, csv_filename=csv_filename)
    except Exception as e:
        error_message = f"Error processing JSON files: {e}\n"
        print(error_message)


# Repeat the process until both directories are empty
while True:
    # Process the files in txts directory
    process_text_files()
    process_json_files()

    # Break the loop if both directories are empty
    if not os.listdir(txt_dir):
        print("All files processed successfully.")
        finalizer.remove_duplicates(csv_filename)
        break
