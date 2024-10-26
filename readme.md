# Text Processing, Summarization and Conversion Tool

## Version: 2.0

## Realse Date: 2024-10-26

This Python project is designed to process text files, summarize their content, and convert the summaries into JSON format. Additionally, the project includes functionality to convert the generated JSON files into a CSV format for easier data management.

## Features

-   **Text File Processing**: Reads text files from a specified directory.
-   **Content Summarization**: Utilizes a summarization function to generate concise summaries of the text.
-   **JSON Conversion**: Saves the summaries in JSON format, ensuring compatibility with various data processing tools.
-   **Error Logging**: Implements error handling with an error log to capture any issues encountered during file processing.
-   **CSV Generation**: Converts the summarized JSON files into a CSV format for easier analysis and reporting.

## Usage

1. Ensure you have the necessary text files in the `txts/` directory.
2. Write any extra append information in `append.txt`.
3. Run the script, and it will:
    - Process each text file in the directory.
    - Summarize the content and save it as JSON.
    - Move processed text files to a designated folder.
    - Convert JSON summaries to a CSV file.

## Note

Before running the script, confirm that the required append information is present in the `append.txt` file.

# Usage Guide

## Step 1: Clone the repository

```bash
git clone
```

### Or download the zip file and extract it.

```bash
https://codeload.github.com/asadali27232/ETL_Pipeline/zip/refs/heads/main

```

## Step 2 Setup python 3.12.x

```bash
https://www.python.org/downloads/release/python-3127/
```

## Step 3: Install the required packages

```bash
pip install -r requirements.txt
```

## Step 4: Get the Gemini API key from the following link

```bash
https://aistudio.google.com/app/apikey
```

## Step 4: Run the pipeline

```bash
python3.12 main.py
```
