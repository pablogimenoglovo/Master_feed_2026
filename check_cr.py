"""Check full Control Room headers."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from google.oauth2 import service_account
from googleapiclient.discovery import build
import warnings
warnings.filterwarnings('ignore')
import string

creds = service_account.Credentials.from_service_account_file(
    r'C:\Users\PabloGimeno\Documents\GitHub\Referral-Calculator\credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)
service = build('sheets', 'v4', credentials=creds)
SID = '1V6q9zAKejMToYd8BiK0P8U42EpTt2tdEnp8u_xCTCN8'

r = service.spreadsheets().values().get(
    spreadsheetId=SID,
    range="'Control Room'!A2:AZ3"
).execute()
rows = r.get('values', [])
sections = rows[0] if rows else []
headers = rows[1] if len(rows) > 1 else []

cols = list(string.ascii_uppercase) + ['A'+c for c in string.ascii_uppercase]
max_len = max(len(sections), len(headers))
for i in range(max_len):
    sec = sections[i] if i < len(sections) else ''
    hdr = headers[i] if i < len(headers) else ''
    if hdr or sec:
        print(f"  {cols[i]:3}: {sec:30} | {hdr}")
