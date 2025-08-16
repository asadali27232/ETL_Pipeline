import re
import os
import json
import shutil
import ai_summerizer.modules.txt_to_json as txt_to_json
import ai_summerizer.modules.json_to_csv as json_to_csv
import ai_summerizer.modules.append as append
import ai_summerizer.modules.finalizer as finalizer


def process_text_files(txt_dir, json_dir, processed_txt_dir):
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
                        print(
                            f"Error decoding JSON for {filename}. Saving raw summary.")
                        summary_json = summary  # Use raw summary if JSON decoding fails

                    # Save the summary to a JSON file
                    with open(json_path, 'w', encoding='utf-8') as file:
                        json.dump(summary_json, file,
                                  ensure_ascii=False, indent=4)

                    print(
                        f"Summarized {filename} and saved summary to {json_filename}")

                    # Move processed text file to the processed folder
                    shutil.move(txt_path, os.path.join(
                        processed_txt_dir, filename))

                except Exception as e:
                    error_message = f"Error summarizing {filename}: {e}\n"
                    print(error_message)

            except Exception as e:
                error_message = f"Error reading {filename}: {e}\n"
                print(error_message)


def process_json_files(json_folder, json_processed_folder, txts_folder, txt_processed_folder, csv_filename, reference_file):
    try:
        json_to_csv.process(json_folder, json_processed_folder, txts_folder,
                            txt_processed_folder, csv_filename, reference_file)
    except Exception as e:
        error_message = f"Error processing JSON files: {e}\n"
        print(error_message)


def run():
    # Define directories
    txt_dir = './ai_summerizer/txts/'
    json_dir = './ai_summerizer/jsons/'
    processed_txt_dir = './ai_summerizer/txt_processed/'
    json_processed_dir = './ai_summerizer/json_processed/'

    reference_file = './ai_summerizer/modules/helpers/reference.json'

    csv_filename = './Updated_Universities/'
    append_filename = './ai_summerizer/modules/helpers/append.txt'

    confirmation = input(
        "Are you sure you have written Extra Append Information (append.txt) in append.txt file? (y/n): ")
    if confirmation.lower() != 'y':
        print("Please write Extra Append Information in append.txt file and run the program again.")
        exit()

    # Get and clean the CSV filename from the user in one line
    csv_filename_imput = re.sub(r'[^a-zA-Z0-9 ]', '', str(input(
        "Enter the name of the current University: ")).strip())

    csv_filename = csv_filename + csv_filename_imput + ' Updated Courses.csv'

    append.append_to_txts(txt_folder=txt_dir, append_file=append_filename)

    print(f"CSV filename set to: {csv_filename}")

    # Create directories if they don't exist
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(processed_txt_dir, exist_ok=True)
    os.makedirs(txt_dir, exist_ok=True)
    os.makedirs(json_processed_dir, exist_ok=True)

    # Repeat the process until both directories are empty
    while True:
        # Process the files in txts directory
        process_text_files(txt_dir, json_dir, processed_txt_dir)
        process_json_files(json_dir, json_processed_dir, txt_dir,
                           processed_txt_dir,  csv_filename, reference_file)

        # Break the loop if both directories are empty
        if not os.listdir(txt_dir):
            print("All files processed successfully.")
            finalizer.remove_duplicates(csv_filename)
            break
