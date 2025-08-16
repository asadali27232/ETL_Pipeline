import os


def append_to_txts(txt_folder="txts", append_file="append.txt"):
    # Read the content of append.txt
    with open(append_file, 'r', encoding='utf-8') as af:
        append_content = af.read()

    # Prepare a set of filenames to skip
    already_appended = set()

    # Loop through all files in the txt folder
    for filename in os.listdir(txt_folder):
        if filename.endswith('.txt'):
            file_path = os.path.join(txt_folder, filename)

            # Check if append_content is already in the current file
            with open(file_path, 'r', encoding='utf-8') as f:
                # Use a small read to check for the existence of the content
                if append_content in f.read():
                    already_appended.add(filename)
                    continue  # Skip this file if content is already present

            # Append only if the content was not found
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write("\n\n\n")  # Add some space before appending
                f.write(append_content)

            print(f"Appended content to {filename}")

    # Print out the files that were skipped
    for skipped_file in already_appended:
        print(f"Extra Append Information already exists in {skipped_file}")


if __name__ == "__main__":
    append_to_txts()
