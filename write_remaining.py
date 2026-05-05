"""Write missing rows from cache to new spreadsheet."""
import pickle
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import warnings
warnings.filterwarnings('ignore')

creds = service_account.Credentials.from_service_account_file(
    r'C:\Users\PabloGimeno\Documents\GitHub\Referral-Calculator\credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
service = build('sheets', 'v4', credentials=creds)
NEW_SID = '1V6q9zAKejMToYd8BiK0P8U42EpTt2tdEnp8u_xCTCN8'

# Load cached data
with open(r'C:\Users\PabloGimeno\Downloads\Master_feed_2026-main\_fixed_data_cache.pkl', 'rb') as f:
    header, fixed_rows = pickle.load(f)

print(f'Cached: {len(fixed_rows)} data rows')
print(f'Expected last sheet row: {len(fixed_rows) + 1}')

# Data currently ends at row 110,419 in the sheet
# Sheet row 110,420 corresponds to all_data index 110,419
all_data = [header] + fixed_rows
start_index = 110419
remaining = all_data[start_index:]
start_row = 110420

print(f'Rows to write: {len(remaining)} (from sheet row {start_row} to {start_row + len(remaining) - 1})')
print(f'First row sample: {remaining[0][:8]}')
print(f'Last row sample: {remaining[-1][:8]}')

# Write in one batch
range_str = f"'Meta Feed_City'!A{start_row}"
print(f'Writing to {range_str}...')

service.spreadsheets().values().update(
    spreadsheetId=NEW_SID,
    range=range_str,
    valueInputOption='USER_ENTERED',
    body={'values': remaining}
).execute()

print('Write complete!')
