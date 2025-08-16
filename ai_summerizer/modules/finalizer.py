import csv
import os


def remove_duplicates(file_path, delimiter=','):
    # Temporary file to hold unique rows before overwriting
    temp_file_path = file_path + '.tmp'
    seen = set()  # A set to track unique values in the first column
    rows = []

    # Read the file and filter out duplicates
    with open(file_path, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter=delimiter)
        header = next(reader, None)  # Read header if it exists

        # Store the header (if it exists)
        if header:
            rows.append(header)

        # Process the remaining rows
        for row in reader:
            if row:  # Ensure the row is not empty
                # Remove leading/trailing spaces
                first_col_value = row[0].strip()
                if first_col_value and first_col_value not in seen:
                    rows.append(row)
                    seen.add(first_col_value)

    # Write the filtered rows back to a temporary file
    with open(temp_file_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter=delimiter)
        writer.writerows(rows)

    # Replace the original file with the cleaned temporary file
    os.replace(temp_file_path, file_path)
    print(f"Duplicates removed successfully and saved to: {file_path}")


if __name__ == '__main__':
    remove_duplicates("output.csv")

