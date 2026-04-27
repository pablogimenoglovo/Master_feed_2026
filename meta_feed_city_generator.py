import csv
import gspread
from google.oauth2.service_account import Credentials
import time
import os

# --- CONFIG ---
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "credentials.json")
SPREADSHEET_ID = "17-Dy3aPCaqCMia51s-7lNAjRmp4wpT2860jhP_PzrZs"
TAB_NAME = "Copy of Meta Feed_City"

CONTROL_ROOM_PATH = r"C:\Users\PabloGimeno\Downloads\Master Feed - 2026 - Control Room.csv"

# --- LANGUAGE MAPPINGS (from URL Generator - mandatory) ---
COUNTRY_LANGUAGES = {
    "BA": ["bs", "en"],
    "ME": ["sr", "en"],
    "MD": ["ro", "ru", "en"],
    "BG": ["bg", "en"],
    "HR": ["hr", "en"],
    "UG": ["en"],
    "RO": ["ro", "en"],
    "RS": ["rs", "en"],
    "KE": ["sw", "en"],
    "NG": ["en"],
    "CI": ["fr", "en"],
    "TN": ["ar", "fr", "en"],
    "MA": ["ar", "en"],
    "PT": ["pt", "en"],
    "AM": ["hy", "ru", "en"],
    "GE": ["ka", "en"],
    "PL": ["pl", "ru", "uk", "en"],
    "KZ": ["kk", "ru", "en"],
    "KG": ["ru", "en"],
    "IT": ["it", "en"],
    "UA": ["uk", "en"],
    "ES": ["es", "en"],
}

# Language code -> Language name mapping
LANGUAGE_NAMES = {
    "bs": "Bosnian",
    "sr": "Serbian",
    "ro": "Romanian",
    "ru": "Russian",
    "bg": "Bulgarian",
    "hr": "Croatian",
    "en": "English",
    "rs": "Serbian",
    "sw": "Swahili",
    "fr": "French",
    "ar": "Arabic",
    "pt": "Portuguese",
    "hy": "Armenian",
    "ka": "Georgian",
    "pl": "Polish",
    "uk": "Ukrainian",
    "kk": "Kazakh",
    "it": "Italian",
    "es": "Spanish",
}

# 10 subtypes x 5 rows each = 50 rows template
TEMPLATE_ROWS = [
    ("General", "A. Icon human"),
    ("General", "A. Icon human"),
    ("General", "A. Icon human"),
    ("General", "A. Icon human"),
    ("General", "A. Icon human"),
    ("General", "A. Vehicle focus"),
    ("General", "A. Vehicle focus"),
    ("General", "A. Vehicle focus"),
    ("General", "A. Vehicle focus"),
    ("General", "A. Vehicle focus"),
    ("General", "A. Referrals"),
    ("General", "A. Referrals"),
    ("General", "A. Referrals"),
    ("General", "A. Referrals"),
    ("General", "A. Referrals"),
    ("General", "A. Local angle"),
    ("General", "A. Local angle"),
    ("General", "A. Local angle"),
    ("General", "A. Local angle"),
    ("General", "A. Local angle"),
    ("Winter", "B. Winter 1"),
    ("Winter", "B. Winter 1"),
    ("Winter", "B. Winter 1"),
    ("Winter", "B. Winter 1"),
    ("Winter", "B. Winter 1"),
    ("Winter", "B. Winter 2"),
    ("Winter", "B. Winter 2"),
    ("Winter", "B. Winter 2"),
    ("Winter", "B. Winter 2"),
    ("Winter", "B. Winter 2"),
    ("Winter", "B. Winter 3"),
    ("Winter", "B. Winter 3"),
    ("Winter", "B. Winter 3"),
    ("Winter", "B. Winter 3"),
    ("Winter", "B. Winter 3"),
    ("Summer", "C. Summer 1"),
    ("Summer", "C. Summer 1"),
    ("Summer", "C. Summer 1"),
    ("Summer", "C. Summer 1"),
    ("Summer", "C. Summer 1"),
    ("Summer", "C. Summer 2"),
    ("Summer", "C. Summer 2"),
    ("Summer", "C. Summer 2"),
    ("Summer", "C. Summer 2"),
    ("Summer", "C. Summer 2"),
    ("Summer", "C. Summer 3"),
    ("Summer", "C. Summer 3"),
    ("Summer", "C. Summer 3"),
    ("Summer", "C. Summer 3"),
    ("Summer", "C. Summer 3"),
]

# Column headers (31 columns: A through AE)
HEADERS = [
    "ID", "helper", "Ad label", "Campaign status", "Ad set status", "Ad status",
    "Country", "City Code", "City size", "Target area", "Budget",
    "Ad type", "Ad subtype", "Ad format",
    "Campaign name", "Ad Set Name", "Ad Name",
    "Language", "Language code",
    "Message", "Title", "Description", "Creative text", "Creative subtitle",
    "CTA", "CTA_Caption", "Square", "Horizontal", "Vertical",
    "CTA_Button", "CTA_Link"
]


def read_control_room(path):
    """Read cities from Control Room CSV (skip first 3 header rows)."""
    cities = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < 3:  # Skip header rows
                continue
            if len(row) >= 3 and row[0].strip():
                city_code = row[0].strip()
                country_code = row[1].strip()
                city_size = row[2].strip() if len(row) > 2 else ""
                cities.append((city_code, country_code, city_size))
    return cities


def generate_rows(cities):
    """Generate all data rows with formulas."""
    all_rows = []
    current_row = 4  # Data starts at row 4 (row 1 = empty/info, row 2 = empty/info, row 3 = headers)

    for city_code, country_code, city_size in cities:
        languages = COUNTRY_LANGUAGES.get(country_code, ["en"])

        for lang_code in languages:
            lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)

            for idx, (ad_type, ad_subtype) in enumerate(TEMPLATE_ROWS):
                row_num = current_row

                # Formulas for Campaign name and Ad Set Name
                campaign_formula = f'="Facebook_Glovers_"&G{row_num}&"_MultiCity_2026"'
                adset_formula = f'=CONCATENATE(G{row_num},"_",H{row_num},"_",L{row_num})'

                # Build row: 31 columns
                row = [
                    "",  # ID
                    "",  # helper
                    "",  # Ad label
                    "",  # Campaign status
                    "",  # Ad set status
                    "",  # Ad status
                    country_code,  # Country (G)
                    city_code,  # City Code (H)
                    city_size,  # City size (I)
                    "",  # Target area (J)
                    "",  # Budget (K)
                    ad_type,  # Ad type (L)
                    ad_subtype,  # Ad subtype (M)
                    "",  # Ad format (N)
                    campaign_formula,  # Campaign name (O)
                    adset_formula,  # Ad Set Name (P)
                    "",  # Ad Name (Q)
                    lang_name,  # Language (R)
                    lang_code,  # Language code (S)
                    "",  # Message (T)
                    "",  # Title (U)
                    "",  # Description (V)
                    "",  # Creative text (W)
                    "",  # Creative subtitle (X)
                    "",  # CTA (Y)
                    "",  # CTA_Caption (Z)
                    "",  # Square (AA)
                    "",  # Horizontal (AB)
                    "",  # Vertical (AC)
                    "",  # CTA_Button (AD)
                    "",  # CTA_Link (AE)
                ]
                all_rows.append(row)
                current_row += 1

    return all_rows


def upload_to_sheets(rows):
    """Upload data to Google Sheets using Sheets API directly for large datasets."""
    from googleapiclient.discovery import build

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scopes)

    service = build("sheets", "v4", credentials=creds)
    sheets = service.spreadsheets()

    # Get sheet ID for the tab
    spreadsheet = sheets.get(spreadsheetId=SPREADSHEET_ID).execute()
    sheet_id = None
    for sheet in spreadsheet["sheets"]:
        if sheet["properties"]["title"] == TAB_NAME:
            sheet_id = sheet["properties"]["sheetId"]
            break

    if sheet_id is None:
        print(f"Tab '{TAB_NAME}' not found! Creating it...")
        body = {
            "requests": [{
                "addSheet": {
                    "properties": {"title": TAB_NAME}
                }
            }]
        }
        resp = sheets.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        sheet_id = resp["replies"][0]["addSheet"]["properties"]["sheetId"]

    # Clear the sheet
    print("Clearing existing data...")
    sheets.values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB_NAME}'!A:AE"
    ).execute()

    # Delete extra rows to free up cells, keep only 1 row
    print("Shrinking sheet to free cells...")
    try:
        sheets.batchUpdate(spreadsheetId=SPREADSHEET_ID, body={
            "requests": [{
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {
                            "rowCount": 1,
                            "columnCount": 31
                        }
                    },
                    "fields": "gridProperties.rowCount,gridProperties.columnCount"
                }
            }]
        }).execute()
    except Exception as e:
        print(f"  Warning shrinking: {e}")

    # Now expand to needed size
    total_rows = len(rows) + 1  # +1 for header
    print(f"Expanding sheet to {total_rows} rows x 31 cols...")
    try:
        sheets.batchUpdate(spreadsheetId=SPREADSHEET_ID, body={
            "requests": [{
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {
                            "rowCount": total_rows,
                            "columnCount": 31
                        }
                    },
                    "fields": "gridProperties.rowCount,gridProperties.columnCount"
                }
            }]
        }).execute()
    except Exception as e:
        print(f"  ERROR expanding: {e}")
        print("  The workbook may have too many cells in other tabs.")
        print("  Trying to write what fits...")

    # Write in batches
    all_data = [HEADERS] + rows
    BATCH_SIZE = 10000

    for start in range(0, len(all_data), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(all_data))
        batch = all_data[start:end]
        start_row = start + 1

        range_str = f"'{TAB_NAME}'!A{start_row}:AE{start_row + len(batch) - 1}"
        print(f"Writing batch: rows {start_row}-{start_row + len(batch) - 1}...")

        try:
            sheets.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=range_str,
                valueInputOption="USER_ENTERED",
                body={"values": batch}
            ).execute()
        except Exception as e:
            print(f"  ERROR writing batch: {e}")
            print("  Retrying in 30s...")
            time.sleep(30)
            try:
                sheets.values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=range_str,
                    valueInputOption="USER_ENTERED",
                    body={"values": batch}
                ).execute()
            except Exception as e2:
                print(f"  FAILED again: {e2}")
                break

        # Rate limiting - Sheets API has 60 requests/min for writes
        if end < len(all_data):
            print("  Waiting 10s for rate limit...")
            time.sleep(10)

    print("Done!")


def main():
    print("Reading Control Room...")
    cities = read_control_room(CONTROL_ROOM_PATH)
    print(f"Found {len(cities)} cities")

    # Count total rows
    total_languages = sum(len(COUNTRY_LANGUAGES.get(c[1], ["en"])) for c in cities)
    total_rows = total_languages * 50
    print(f"Total language slots: {total_languages}")
    print(f"Total rows to generate: {total_rows}")

    print("\nGenerating rows...")
    rows = generate_rows(cities)
    print(f"Generated {len(rows)} rows")

    print("\nUploading to Google Sheets...")
    upload_to_sheets(rows)


if __name__ == "__main__":
    main()
