"""Final integrity check - verify 5-row fix still intact."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from google.oauth2 import service_account
from googleapiclient.discovery import build
import warnings
warnings.filterwarnings('ignore')
from collections import Counter
import time

creds = service_account.Credentials.from_service_account_file(
    r'C:\Users\PabloGimeno\Documents\GitHub\Referral-Calculator\credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)
service = build('sheets', 'v4', credentials=creds)
SID = '1V6q9zAKejMToYd8BiK0P8U42EpTt2tdEnp8u_xCTCN8'

GENERAL = {'Icon_Human', 'Vehicle', 'Referrals', 'Local'}
CL = {
    'BA': ['bs','en'], 'ME': ['sr','en'], 'MD': ['ro','ru','en'],
    'BG': ['bg','en'], 'HR': ['hr','en'], 'UG': ['en'],
    'RO': ['ro','en'], 'RS': ['rs','en'], 'KE': ['sw','en'],
    'NG': ['en'], 'CI': ['fr','en'], 'TN': ['ar','fr','en'],
    'MA': ['ar','en'], 'PT': ['pt','en'], 'AM': ['hy','ru','en'],
    'GE': ['ka','en'], 'PL': ['pl','ru','uk','en'],
    'KZ': ['kk','ru','en'], 'KG': ['ru','en'], 'IT': ['it','en'],
    'UA': ['uk','en'], 'ES': ['es','en'],
}

# Check 6 evenly-spaced regions
checks = [
    (2, 4001, 'MA start'),
    (15001, 18000, 'PL region'),
    (35001, 38000, 'RO/BG region'),
    (55001, 58000, 'IT region'),
    (80001, 83000, 'PT/ES region'),
    (107001, 110000, 'ES end'),
]

total_bugs = 0
total_rows_checked = 0

for start, end, label in checks:
    r = service.spreadsheets().values().get(
        spreadsheetId=SID,
        range=f'Meta Feed_City!G{start}:S{end}'
    ).execute()
    rows = r.get('values', [])

    c = Counter()
    cc = {}
    for row in rows:
        if len(row) > 12 and row[1]:
            c[(row[1], row[12], row[6])] += 1
            cc[row[1]] = row[0]

    bugs = 0
    for k, v in c.items():
        if v == 4 and k[2] in GENERAL:
            country = cc.get(k[0], '')
            first_lang = CL.get(country, ['en'])[0]
            if k[1] != first_lang:
                bugs += 1

    total_bugs += bugs
    total_rows_checked += len(rows)
    print(f"  {label:15} (rows {start}-{end}): {len(rows):5} rows, bugs: {bugs}")
    time.sleep(1)

print(f"\n{'='*50}")
print(f"TOTAL ROWS CHECKED: {total_rows_checked}")
print(f"TOTAL BUGS REMAINING: {total_bugs}")
print(f"STATUS: {'✅ ALL CLEAR' if total_bugs == 0 else '❌ ISSUES FOUND'}")

# Also verify column A-F continuity
print(f"\n--- Column A-F continuity check ---")
for row_num in [2, 50000, 80000, 110419]:
    r = service.spreadsheets().values().get(
        spreadsheetId=SID,
        range=f'Meta Feed_City!A{row_num}:C{row_num}'
    ).execute()
    rows = r.get('values', [])
    data = rows[0] if rows else ['EMPTY']
    print(f"  Row {row_num:>6}: {data}")
