import os
import re
import io
import gspread
import pandas as pd
from tqdm import tqdm
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from gspread_dataframe import get_as_dataframe
from googleapiclient.errors import HttpError

# ---------------------------
# Configurations
# ---------------------------
SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
OUTPUT_DIR = "Downloaded_Universities"

SHEET_ID = "1eYz8Nvr3BToRrmReXNLR8zQrk4X8tsdKZO_Fj9mNThc"
SHEET_NAME = "Updating"
CSV_COLUMN = "CSV"   # Name of the column that has Drive folder links

# ---------------------------
# Authenticate Google APIs
# ---------------------------
try:
    # GSpread
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sh = gc.open_by_key(SHEET_ID)
    ws = sh.worksheet(SHEET_NAME)
    df = get_as_dataframe(ws, evaluate_formulas=True, header=0)

    # Drive
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    drive_service = build('drive', 'v3', credentials=creds)

except Exception as e:
    raise SystemExit(f"❌ Failed to authenticate: {e}")

# ---------------------------
# Extract all folder URLs
# ---------------------------
folder_urls = df[CSV_COLUMN].dropna().tolist()
print(f"📑 Found {len(folder_urls)} folder links in sheet.\n")

# ---------------------------
# Utility: Extract folder ID
# ---------------------------


def extract_folder_id(url: str):
    # Case 1: /folders/<ID>
    match = re.search(r"/folders/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)

    # Case 2: open?id=<ID>
    match = re.search(r"id=([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)

    return None


# ---------------------------
# Utility: Download one folder
# ---------------------------


def download_folder(folder_id, output_base):
    try:
        query = f"'{folder_id}' in parents and trashed=false"
        results = drive_service.files().list(
            q=query,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True
        ).execute()
        items = results.get('files', [])
    except HttpError as e:
        print(f"⚠️ Failed to list folder {folder_id}: {e}")
        return

    if not items:
        print(f"📂 Folder {folder_id} is empty.")
        return

    folder_dir = os.path.join(output_base, folder_id)
    os.makedirs(folder_dir, exist_ok=True)

    for item in items:
        file_name = item['name']
        file_id = item['id']
        mime_type = item['mimeType']

        try:
            # Google Sheet → export as CSV
            if mime_type == 'application/vnd.google-apps.spreadsheet':
                request = drive_service.files().export_media(
                    fileId=file_id, mimeType='text/csv')
                csv_file_name = file_name + ".csv"

            # Normal CSV file
            elif mime_type == 'text/csv':
                request = drive_service.files().get_media(fileId=file_id)
                csv_file_name = file_name

            else:
                continue  # skip non-CSV

            file_path = os.path.join(folder_dir, csv_file_name)

            with io.FileIO(file_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()

        except HttpError as e:
            print(f"⚠️ Error downloading {file_name}: {e}")
            continue


# ---------------------------
# Main Loop: Process all folders with tqdm
# ---------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

for url in tqdm(folder_urls, desc="Processing folders", unit="folder"):
    folder_id = extract_folder_id(url)
    if not folder_id:
        print(f"⚠️  Invalid folder link: {url}")
        continue

    folder_dir = os.path.join(OUTPUT_DIR, folder_id)

    # ✅ Skip only if folder exists AND has at least 1 file
    if os.path.exists(folder_dir) and any(os.scandir(folder_dir)):
        print(f"⏭️  Skipping folder {folder_id} (already downloaded).")
        continue
    else:
        print(f"🔄 Re-downloading folder {folder_id} (empty or missing).")

    download_folder(folder_id, OUTPUT_DIR)

print("\n✅ All CSVs and Google Sheets have been downloaded successfully!")


print("\n✅ All CSVs and Google Sheets have been downloaded successfully!")
