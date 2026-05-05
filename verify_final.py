"""Quick verification of complete rows."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from google.oauth2 import service_account
from googleapiclient.discovery import build
import warnings
warnings.filterwarnings('ignore')

creds = service_account.Credentials.from_service_account_file(
    r'C:\Users\PabloGimeno\Documents\GitHub\Referral-Calculator\credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)
service = build('sheets', 'v4', credentials=creds)
SID = '1V6q9zAKejMToYd8BiK0P8U42EpTt2tdEnp8u_xCTCN8'

# Check a few complete rows at different positions
checks = [
    ('Meta Feed_City!A2:S7', 'Start (rows 2-7)'),
    ('Meta Feed_City!A50000:S50005', 'Middle (rows 50000-50005)'),
    ('Meta Feed_City!A110415:S110419', 'End (rows 110415-110419)'),
]

for rng, label in checks:
    r = service.spreadsheets().values().get(spreadsheetId=SID, range=rng).execute()
    rows = r.get('values', [])
    print(f"\n=== {label} ===")
    for row in rows:
        # Pad to 19 cols
        while len(row) < 19:
            row.append('')
        id_val = row[0]
        helper = row[1]
        ad_label = row[2]
        camp_status = row[3]
        adset_status = row[4]
        ad_status = row[5]
        country = row[6]
        city = row[7]
        ad_type = row[11]
        subtype = row[12]
        lang = row[17]
        lang_code = row[18]
        print(f"  ID={id_val:6} hlp={helper:5} | {country}/{city} | {ad_type:8}/{subtype:12} | {lang}/{lang_code} | D={camp_status} E={adset_status} F={ad_status}")
