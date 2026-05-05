"""
Fix Meta Feed_City: Add missing 5th row for General subtypes in non-first languages.

Bug: In the original sheet, General subtypes (Icon_Human, Vehicle, Referrals, Local)
have only 4 rows instead of 5 in every non-first language for each city.

Fix: Duplicate the last row of each affected group to create the missing 5th row.
Write corrected data to new spreadsheet.
"""

import time
import warnings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from collections import defaultdict

warnings.filterwarnings('ignore')

CREDENTIALS_PATH = r'C:\Users\PabloGimeno\Documents\GitHub\Referral-Calculator\credentials.json'
ORIGINAL_SID = '17-Dy3aPCaqCMia51s-7lNAjRmp4wpT2860jhP_PzrZs'
NEW_SID = '1V6q9zAKejMToYd8BiK0P8U42EpTt2tdEnp8u_xCTCN8'
TAB_NAME = 'Meta Feed_City'

# Column indices (0-based) in the 43-column layout
COL_COUNTRY = 6   # G
COL_CITY = 7      # H
COL_AD_SUBTYPE = 12  # M
COL_LANG_CODE = 18   # S

GENERAL_SUBTYPES = {'Icon_Human', 'Vehicle', 'Referrals', 'Local'}

# Country -> ordered languages (first language is correct, rest have the bug)
COUNTRY_LANGUAGES = {
    "BA": ["bs", "en"], "ME": ["sr", "en"], "MD": ["ro", "ru", "en"],
    "BG": ["bg", "en"], "HR": ["hr", "en"], "UG": ["en"],
    "RO": ["ro", "en"], "RS": ["rs", "en"], "KE": ["sw", "en"],
    "NG": ["en"], "CI": ["fr", "en"], "TN": ["ar", "fr", "en"],
    "MA": ["ar", "en"], "PT": ["pt", "en"], "AM": ["hy", "ru", "en"],
    "GE": ["ka", "en"], "PL": ["pl", "ru", "uk", "en"],
    "KZ": ["kk", "ru", "en"], "KG": ["ru", "en"], "IT": ["it", "en"],
    "UA": ["uk", "en"], "ES": ["es", "en"],
}


def get_service():
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return build('sheets', 'v4', credentials=creds)


def read_all_data(service):
    """Read all data from original sheet in batches."""
    print("Reading data from original sheet...")
    all_rows = []
    batch_size = 10000
    start_row = 1  # Row 1 = header

    # First read header
    result = service.spreadsheets().values().get(
        spreadsheetId=ORIGINAL_SID,
        range=f"'{TAB_NAME}'!A1:AQ1"
    ).execute()
    header = result.get('values', [[]])[0]
    print(f"  Header: {len(header)} columns")

    # Read data in batches starting from row 2
    row_offset = 2
    while True:
        range_str = f"'{TAB_NAME}'!A{row_offset}:AQ{row_offset + batch_size - 1}"
        result = service.spreadsheets().values().get(
            spreadsheetId=ORIGINAL_SID,
            range=range_str
        ).execute()
        rows = result.get('values', [])

        if not rows:
            break

        all_rows.extend(rows)
        print(f"  Read {len(all_rows)} rows so far (batch from row {row_offset})...")
        row_offset += batch_size

        # Small delay to avoid rate limiting on reads
        time.sleep(2)

    print(f"  Total data rows read: {len(all_rows)}")
    return header, all_rows


def fix_data(header, rows):
    """Fix the 4-row bug by adding missing 5th rows for General subtypes."""
    print("\nFixing data...")

    # Group rows by (city, language_code)
    # We process sequentially to maintain order
    fixed_rows = []
    i = 0
    total_added = 0
    cities_processed = 0

    while i < len(rows):
        row = rows[i]

        # Pad row to full width if needed
        while len(row) < len(header):
            row.append('')

        # Get current city and language
        city = row[COL_CITY] if len(row) > COL_CITY else ''
        lang = row[COL_LANG_CODE] if len(row) > COL_LANG_CODE else ''
        country = row[COL_COUNTRY] if len(row) > COL_COUNTRY else ''

        # Collect all rows for this city+language block
        block = []
        while i < len(rows):
            r = rows[i]
            while len(r) < len(header):
                r.append('')
            r_city = r[COL_CITY] if len(r) > COL_CITY else ''
            r_lang = r[COL_LANG_CODE] if len(r) > COL_LANG_CODE else ''
            if r_city == city and r_lang == lang:
                block.append(r)
                i += 1
            else:
                break

        # Determine if this is a non-first language
        first_lang = COUNTRY_LANGUAGES.get(country, ['en'])[0]
        is_non_first = (lang != first_lang)

        if is_non_first and city and lang:
            # Check each General subtype in this block
            subtype_groups = defaultdict(list)
            for r in block:
                subtype = r[COL_AD_SUBTYPE] if len(r) > COL_AD_SUBTYPE else ''
                subtype_groups[subtype].append(r)

            # Rebuild block with fixes
            new_block = []
            for r in block:
                new_block.append(r)
                subtype = r[COL_AD_SUBTYPE] if len(r) > COL_AD_SUBTYPE else ''

                # If this is the last row of a General subtype group with only 4 rows,
                # duplicate it to make 5
                if subtype in GENERAL_SUBTYPES:
                    group = subtype_groups[subtype]
                    if len(group) == 4 and r is group[-1]:
                        # Add a duplicate of this row as the 5th
                        new_block.append(list(r))
                        total_added += 1

            fixed_rows.extend(new_block)
        else:
            # First language or single-language - keep as-is
            fixed_rows.extend(block)

        cities_processed += 1
        if cities_processed % 500 == 0:
            print(f"  Processed {cities_processed} city-lang blocks, added {total_added} rows...")

    print(f"  Done. Total rows added: {total_added}")
    print(f"  Original rows: {len(rows)}")
    print(f"  Fixed rows: {len(fixed_rows)}")
    return fixed_rows


def write_to_new_sheet(service, header, fixed_rows):
    """Write corrected data to new spreadsheet."""
    print(f"\nWriting to new spreadsheet...")
    sheets = service.spreadsheets()

    # Get sheet ID
    spreadsheet = sheets.get(spreadsheetId=NEW_SID).execute()
    sheet_id = None
    for sheet in spreadsheet['sheets']:
        if sheet['properties']['title'] == TAB_NAME:
            sheet_id = sheet['properties']['sheetId']
            break

    if sheet_id is None:
        print(f"  ERROR: Tab '{TAB_NAME}' not found!")
        return

    # Resize sheet - shrink to 1 row first (this implicitly clears all data)
    total_rows = len(fixed_rows) + 1  # +1 for header
    num_cols = len(header)

    print("  Shrinking sheet to 1x1 (clears data)...")
    try:
        sheets.batchUpdate(spreadsheetId=NEW_SID, body={
            "requests": [{
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {"rowCount": 1, "columnCount": 1}
                    },
                    "fields": "gridProperties.rowCount,gridProperties.columnCount"
                }
            }]
        }).execute()
        time.sleep(3)
        print("  Shrink complete.")
    except Exception as e:
        print(f"  Warning shrinking: {e}")

    print(f"  Expanding to {total_rows} rows x {num_cols} cols...")

    # Expand
    try:
        sheets.batchUpdate(spreadsheetId=NEW_SID, body={
            "requests": [{
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {"rowCount": total_rows, "columnCount": num_cols}
                    },
                    "fields": "gridProperties.rowCount,gridProperties.columnCount"
                }
            }]
        }).execute()
        time.sleep(2)
    except Exception as e:
        print(f"  ERROR expanding: {e}")
        return

    # Write in batches
    all_data = [header] + fixed_rows
    BATCH_SIZE = 10000

    for start in range(0, len(all_data), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(all_data))
        batch = all_data[start:end]
        start_row = start + 1

        range_str = f"'{TAB_NAME}'!A{start_row}"
        print(f"  Writing batch: rows {start_row}-{start_row + len(batch) - 1}...")

        try:
            sheets.values().update(
                spreadsheetId=NEW_SID,
                range=range_str,
                valueInputOption="USER_ENTERED",
                body={"values": batch}
            ).execute()
        except Exception as e:
            print(f"  ERROR: {e}")
            print("  Retrying in 30s...")
            time.sleep(30)
            try:
                sheets.values().update(
                    spreadsheetId=NEW_SID,
                    range=range_str,
                    valueInputOption="USER_ENTERED",
                    body={"values": batch}
                ).execute()
            except Exception as e2:
                print(f"  FAILED: {e2}")
                return

        if end < len(all_data):
            print("  Waiting 10s for rate limit...")
            time.sleep(10)

    print("\nWrite complete!")
    print(f"Total rows written: {len(all_data)} (1 header + {len(fixed_rows)} data)")


def main():
    import pickle
    import os

    cache_file = os.path.join(os.path.dirname(__file__), '_fixed_data_cache.pkl')
    service = get_service()

    if os.path.exists(cache_file):
        print("Loading cached fixed data...")
        with open(cache_file, 'rb') as f:
            header, fixed_rows = pickle.load(f)
        print(f"  Loaded: {len(fixed_rows)} rows")
    else:
        # Step 1: Read all data
        header, rows = read_all_data(service)

        # Step 2: Fix the bug
        fixed_rows = fix_data(header, rows)

        # Cache for retry
        with open(cache_file, 'wb') as f:
            pickle.dump((header, fixed_rows), f)
        print(f"  Cached fixed data for retry.")

    # Step 3: Write to new sheet
    write_to_new_sheet(service, header, fixed_rows)


if __name__ == '__main__':
    main()
