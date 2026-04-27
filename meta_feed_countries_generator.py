import csv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import time
import os

# --- CONFIG ---
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "credentials.json")
SPREADSHEET_ID = "17-Dy3aPCaqCMia51s-7lNAjRmp4wpT2860jhP_PzrZs"
TAB_NAME = "Copy of Meta Feed_Countries"

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

# All 22 unique countries
COUNTRIES = list(COUNTRY_LANGUAGES.keys())

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

# Column headers (29 columns: A through AC)
HEADERS = [
    "ID", "helper", "Ad label", "Campaign status", "Ad set status", "Ad status",
    "Country", "Target area", "Budget",
    "Ad type", "Ad subtype", "Ad format",
    "Campaign name", "Ad Set Name", "Ad Name",
    "Language", "Language code",
    "Message", "Title", "Description", "Creative text", "Creative subtitle",
    "CTA", "CTA_Caption", "Square", "Horizontal", "Vertical",
    "CTA_Button", "CTA_Link"
]


def generate_rows():
    """Generate all data rows with formulas for countries."""
    all_rows = []
    current_row = 2  # Data starts at row 2 (row 1 = headers)

    for country_code in COUNTRIES:
        languages = COUNTRY_LANGUAGES[country_code]

        for lang_code in languages:
            lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)

            for idx, (ad_type, ad_subtype) in enumerate(TEMPLATE_ROWS):
                row_num = current_row

                # Formulas for Campaign name and Ad Set Name
                # Campaign: ="Facebook_Glovers_"&G{row}&"_Country_2026"
                campaign_formula = f'="Facebook_Glovers_"&G{row_num}&"_Country_2026"'
                # Ad Set Name: =CONCATENATE(G{row},"_",J{row})
                adset_formula = f'=CONCATENATE(G{row_num},"_",J{row_num})'

                # Build row: 29 columns
                row = [
                    "",  # ID (A)
                    "",  # helper (B)
                    "",  # Ad label (C)
                    "",  # Campaign status (D)
                    "",  # Ad set status (E)
                    "",  # Ad status (F)
                    country_code,  # Country (G)
                    "",  # Target area (H)
                    "",  # Budget (I)
                    ad_type,  # Ad type (J)
                    ad_subtype,  # Ad subtype (K)
                    "",  # Ad format (L)
                    campaign_formula,  # Campaign name (M)
                    adset_formula,  # Ad Set Name (N)
                    "",  # Ad Name (O)
                    lang_name,  # Language (P)
                    lang_code,  # Language code (Q)
                    "",  # Message (R)
                    "",  # Title (S)
                    "",  # Description (T)
                    "",  # Creative text (U)
                    "",  # Creative subtitle (V)
                    "",  # CTA (W)
                    "",  # CTA_Caption (X)
                    "",  # Square (Y)
                    "",  # Horizontal (Z)
                    "",  # Vertical (AA)
                    "",  # CTA_Button (AB)
                    "",  # CTA_Link (AC)
                ]
                all_rows.append(row)
                current_row += 1

    return all_rows


def upload_to_sheets(rows):
    """Upload data to Google Sheets."""
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

    # Shrink sheet to 1 row first to free cells across workbook
    print("Shrinking sheet to free cells...")
    sheets.values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB_NAME}'!A:ZZ"
    ).execute()

    sheets.batchUpdate(spreadsheetId=SPREADSHEET_ID, body={
        "requests": [{
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {
                        "rowCount": 1,
                        "columnCount": 1
                    }
                },
                "fields": "gridProperties.rowCount,gridProperties.columnCount"
            }
        }]
    }).execute()

    # Now expand to needed size
    total_rows = len(rows) + 1
    print(f"Expanding to {total_rows} rows x 29 cols...")
    sheets.batchUpdate(spreadsheetId=SPREADSHEET_ID, body={
        "requests": [{
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {
                        "rowCount": total_rows,
                        "columnCount": 29
                    }
                },
                "fields": "gridProperties.rowCount,gridProperties.columnCount"
            }
        }]
    }).execute()

    # Write all data at once (small enough ~2750 rows)
    all_data = [HEADERS] + rows
    range_str = f"'{TAB_NAME}'!A1:AC{len(all_data)}"
    print(f"Writing {len(all_data)} rows...")

    sheets.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_str,
        valueInputOption="USER_ENTERED",
        body={"values": all_data}
    ).execute()

    print("Done!")


def main():
    print("Generating country rows...")
    rows = generate_rows()

    total_languages = sum(len(langs) for langs in COUNTRY_LANGUAGES.values())
    print(f"Countries: {len(COUNTRIES)}")
    print(f"Total language slots: {total_languages}")
    print(f"Total rows generated: {len(rows)}")

    print("\nUploading to Google Sheets...")
    upload_to_sheets(rows)


if __name__ == "__main__":
    main()
