"""
Regenerate columns A-F for ALL rows in the new Meta Feed_City sheet.

Existing columns G-AQ are already correct (with the 4→5 fix applied).
This script writes ONLY columns A-F with proper values and formulas.

Column mapping:
  A (ID): Sequential number 1, 2, 3...
  B (helper): Cycles every 5 rows: ((ID-1)//5)+1
  C (Ad label): "Ad " + helper
  D (Campaign status): =XLOOKUP(H{row},'Control Room'!$A:$A,'Control Room'!$G:$G)
  E (Ad set status): =IFS based on Ad type (L) → Control Room Q/R/S
  F (Ad status): =IFS based on Ad subtype (M) → Control Room T-AC
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import warnings
warnings.filterwarnings('ignore')

CREDENTIALS_PATH = r'C:\Users\PabloGimeno\Documents\GitHub\Referral-Calculator\credentials.json'
NEW_SID = '1V6q9zAKejMToYd8BiK0P8U42EpTt2tdEnp8u_xCTCN8'
TAB_NAME = 'Meta Feed_City'

# Last data row (verified earlier)
LAST_DATA_ROW = 110419
TOTAL_DATA_ROWS = LAST_DATA_ROW - 1  # 110418 (row 2 to 110419)


def get_service():
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return build('sheets', 'v4', credentials=creds)


def generate_af_rows():
    """Generate columns A-F for all data rows."""
    print(f"Generating A-F for {TOTAL_DATA_ROWS} rows...")
    rows = []

    for row_num in range(2, LAST_DATA_ROW + 1):  # Sheet rows 2 to 110419
        row_id = row_num - 1  # ID starts at 1
        helper = ((row_id - 1) // 5) + 1
        ad_label = f"Ad {helper}"

        # Campaign status formula: lookup Meta activity flag from Control Room
        campaign_formula = (
            f"=IFERROR(XLOOKUP(H{row_num},'Control Room'!$A:$A,'Control Room'!$G:$G),\"\")"
        )

        # Ad set status formula: based on Ad type (column L)
        adset_formula = (
            f"=IFERROR(IFS("
            f"L{row_num}=\"General\",XLOOKUP(H{row_num},'Control Room'!$A:$A,'Control Room'!$Q:$Q),"
            f"L{row_num}=\"Winter\",XLOOKUP(H{row_num},'Control Room'!$A:$A,'Control Room'!$R:$R),"
            f"L{row_num}=\"Summer\",XLOOKUP(H{row_num},'Control Room'!$A:$A,'Control Room'!$S:$S)"
            f"),\"\")"
        )

        # Ad status formula: based on Ad subtype (column M)
        ad_status_formula = (
            f"=IFERROR(IFS("
            f"M{row_num}=\"Icon_Human\",XLOOKUP(H{row_num},'Control Room'!$A:$A,'Control Room'!$T:$T),"
            f"M{row_num}=\"Vehicle\",XLOOKUP(H{row_num},'Control Room'!$A:$A,'Control Room'!$U:$U),"
            f"M{row_num}=\"Referrals\",XLOOKUP(H{row_num},'Control Room'!$A:$A,'Control Room'!$V:$V),"
            f"M{row_num}=\"Local\",XLOOKUP(H{row_num},'Control Room'!$A:$A,'Control Room'!$W:$W),"
            f"M{row_num}=\"Winter 1\",XLOOKUP(H{row_num},'Control Room'!$A:$A,'Control Room'!$X:$X),"
            f"M{row_num}=\"Winter 2\",XLOOKUP(H{row_num},'Control Room'!$A:$A,'Control Room'!$Y:$Y),"
            f"M{row_num}=\"Winter 3\",XLOOKUP(H{row_num},'Control Room'!$A:$A,'Control Room'!$Z:$Z),"
            f"M{row_num}=\"Summer 1\",XLOOKUP(H{row_num},'Control Room'!$A:$A,'Control Room'!$AA:$AA),"
            f"M{row_num}=\"Summer 2\",XLOOKUP(H{row_num},'Control Room'!$A:$A,'Control Room'!$AB:$AB),"
            f"M{row_num}=\"Summer 3\",XLOOKUP(H{row_num},'Control Room'!$A:$A,'Control Room'!$AC:$AC)"
            f"),\"\")"
        )

        rows.append([
            str(row_id),        # A: ID
            str(helper),        # B: helper
            ad_label,           # C: Ad label
            campaign_formula,   # D: Campaign status
            adset_formula,      # E: Ad set status
            ad_status_formula,  # F: Ad status
        ])

        if len(rows) % 50000 == 0:
            print(f"  Generated {len(rows)} rows...")

    print(f"  Done. Generated {len(rows)} rows.")
    return rows


def write_af_columns(service, rows):
    """Write columns A-F in batches."""
    print(f"\nWriting columns A-F to new sheet...")
    sheets = service.spreadsheets()

    BATCH_SIZE = 5000  # Smaller batches since formulas are large

    for start in range(0, len(rows), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(rows))
        batch = rows[start:end]
        sheet_start_row = start + 2  # Data starts at row 2

        range_str = f"'{TAB_NAME}'!A{sheet_start_row}:F{sheet_start_row + len(batch) - 1}"
        print(f"  Writing batch: rows {sheet_start_row}-{sheet_start_row + len(batch) - 1}...")

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
                return False

        if end < len(rows):
            time.sleep(10)

    print("\nWrite complete!")
    return True


def main():
    service = get_service()

    # Generate A-F values
    rows = generate_af_rows()

    # Write to sheet
    success = write_af_columns(service, rows)

    if success:
        print(f"\nDone! Columns A-F written for all {TOTAL_DATA_ROWS} rows.")
    else:
        print("\nFailed! Check errors above.")


if __name__ == '__main__':
    main()
