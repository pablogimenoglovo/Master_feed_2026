# Meta Feed Generator — Knowledge Base

## Overview

This project generates Meta (Facebook) advertising feed spreadsheets for Glovo's referral/growth campaigns. It programmatically creates rows in Google Sheets using the Sheets API, multiplying ad templates by countries, cities, and languages.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Sheets Workbook                     │
│  ID: 17-Dy3aPCaqCMia51s-7lNAjRmp4wpT2860jhP_PzrZs          │
├─────────────────────────────────────────────────────────────┤
│  Copy of Meta Feed_City      → 111,350 rows (city-level)    │
│  Copy of Meta Feed_Countries → 2,400 rows (country-level)   │
│  Control Room                → 952 cities (source data)     │
│  geo_helper                  → 228K rows (5.9M cells!)      │
│  + 14 other tabs                                             │
└─────────────────────────────────────────────────────────────┘
         ▲
         │ Google Sheets API v4 (service account)
         │
┌────────┴────────────────────────────────────────────────────┐
│  Scripts (Python 3.9.13)                                     │
│                                                              │
│  meta_feed_city_generator.py      → City feed (952 cities)  │
│  meta_feed_countries_generator.py → Country feed (22 countries)│
└─────────────────────────────────────────────────────────────┘
         ▲
         │ Reads source data from
         │
┌────────┴────────────────────────────────────────────────────┐
│  Source Files (Downloads folder)                             │
│                                                              │
│  Master Feed - 2026 - Control Room.csv      → 952 cities    │
│  DH Migration - UTMs - Global URL Generator (2).csv         │
│  Master Feed _ Vol 3 - Capital_feed (1).csv                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Credentials

- **File**: `C:\Users\PabloGimeno\Documents\GitHub\Referral-Calculator\credentials.json`
- **Service account**: `fsp-growth-bot@dhub-glovo.iam.gserviceaccount.com`
- **Project**: `dhub-glovo`
- **Scopes needed**: `spreadsheets`, `drive`

---

## Scripts

### `meta_feed_city_generator.py`

**Purpose**: Generates city-level Meta ad feed rows.

**Output**: "Copy of Meta Feed_City" tab — 111,350 rows

**Logic**:
- 952 cities (from Control Room) × languages per country × 50 ad template rows
- 31 columns (includes City Code, City Size columns that country version doesn't have)

**Key formulas**:
- Campaign name: `="Facebook_Glovers_"&G{row}&"_MultiCity_2026"`
- Ad Set Name: `=CONCATENATE(G{row},"_",H{row},"_",L{row})` — NO trailing underscore, NO language code

**Batch writing**: Writes in batches of 10,000 rows with 10s rate-limit delays (needed for 111K rows).

---

### `meta_feed_countries_generator.py`

**Purpose**: Generates country-level Meta ad feed rows.

**Output**: "Copy of Meta Feed_Countries" tab — 2,400 rows

**Logic**:
- 22 countries × languages per country (48 total slots) × 50 ad template rows
- 29 columns

**Key formulas**:
- Campaign name: `="Facebook_Glovers_"&G{row}&"_Country_2026"`
- Ad Set Name: `=CONCATENATE(G{row},"_",J{row})` → produces e.g. `AM_General`, `PL_Winter`

**Single write**: Small enough to upload in one API call.

---

## The 50-Row Template (per city/country per language)

10 ad subtypes × 5 rows each = 50 rows:

| Ad Type  | Ad Subtype      | Rows |
|----------|-----------------|------|
| General  | A. Icon human   | 5    |
| General  | A. Vehicle focus| 5    |
| General  | A. Referrals    | 5    |
| General  | A. Local angle  | 5    |
| Winter   | B. Winter 1     | 5    |
| Winter   | B. Winter 2     | 5    |
| Winter   | B. Winter 3     | 5    |
| Summer   | C. Summer 1     | 5    |
| Summer   | C. Summer 2     | 5    |
| Summer   | C. Summer 3     | 5    |

---

## Country → Language Mappings (MANDATORY)

Source: **Global URL Generator** file. This is the authoritative source. Never use Capital_feed as primary.

```
BA → bs, en
ME → sr, en
MD → ro, ru, en
BG → bg, en
HR → hr, en
UG → en
RO → ro, en
RS → rs, en
KE → sw, en
NG → en
CI → fr, en
TN → ar, fr, en
MA → ar, en
PT → pt, en
AM → hy, ru, en
GE → ka, en
PL → pl, ru, uk, en
KZ → kk, ru, en
KG → ru, en
IT → it, en
UA → uk, en
ES → es, en
```

**Language names** (used in the "Language" column):
```
bs=Bosnian, sr=Serbian, ro=Romanian, ru=Russian, bg=Bulgarian,
hr=Croatian, en=English, rs=Serbian, sw=Swahili, fr=French,
ar=Arabic, pt=Portuguese, hy=Armenian, ka=Georgian, pl=Polish,
uk=Ukrainian, kk=Kazakh, it=Italian, es=Spanish
```

---

## Column Layouts

### City Feed (31 columns)

```
ID, helper, Ad label, Campaign status, Ad set status, Ad status,
Country, City Code, City Size, Target area, Budget,
Ad type, Ad subtype, Ad format,
Campaign name, Ad Set Name, Ad Name,
Language, Language code,
Message, Title, Description, Creative text, Creative subtitle,
CTA, CTA_Caption, Square, Horizontal, Vertical,
CTA_Button, CTA_Link
```

### Country Feed (29 columns)

```
ID, helper, Ad label, Campaign status, Ad set status, Ad status,
Country, Target area, Budget,
Ad type, Ad subtype, Ad format,
Campaign name, Ad Set Name, Ad Name,
Language, Language code,
Message, Title, Description, Creative text, Creative subtitle,
CTA, CTA_Caption, Square, Horizontal, Vertical,
CTA_Button, CTA_Link
```

**Difference**: Country feed has NO "City Code" or "City Size" columns.

---

## Critical Constraints

### 10 Million Cell Limit

The Google Sheets workbook has a **hard 10M cell limit**. As of now:
- `geo_helper` tab: **5,946,824 cells** (228K rows × 26 cols)
- `Copy of Meta Feed_City`: **3,451,881 cells** (111K rows × 31 cols)
- Everything else: ~500K cells
- **Total: ~9.9M / 10M**

**Before any write operation**, you MUST:
1. Shrink the target tab to 1×1 first (frees its cells)
2. If still not enough, shrink other unused tabs (e.g., "Meta Feed_City", "Meta Feed_Countries" originals were shrunk to 1×1)
3. Only then expand and write

**Strategy that works**:
```python
# 1. Clear content
sheets.values().clear(range="'TabName'!A:ZZ")
# 2. Shrink to 1x1
batchUpdate → gridProperties: rowCount=1, columnCount=1
# 3. Expand to needed size
batchUpdate → gridProperties: rowCount=N, columnCount=M
# 4. Write data
sheets.values().update(...)
```

### Rate Limits

For large uploads (>10K rows), batch in chunks of 10,000 with `time.sleep(10)` between batches.

### Formula Syntax

- Use `USER_ENTERED` as `valueInputOption` so formulas are evaluated
- Formulas reference their own row number (calculated during generation)
- Row numbering starts at 2 (row 1 = headers)

---

## Source Files Location

All source CSVs are in `C:\Users\PabloGimeno\Downloads\`:

| File | Purpose |
|------|---------|
| `Master Feed - 2026 - Control Room.csv` | 952 cities with country codes, city sizes |
| `DH Migration - UTMs - Global URL Generator (2).csv` | Country → language mappings (MANDATORY) |
| `Master Feed _ Vol 3 - Capital_feed (1).csv` | Language name/code reference |
| `Master Feed - 2026 - Meta Feed_Countries.csv` | Original template (29 columns) |

---

## Python Dependencies

```
google-auth
google-api-python-client
gspread (installed but NOT used — Sheets API v4 direct is preferred)
```

**Why not gspread?** It doesn't handle the 10M cell limit well. Direct Sheets API gives more control over grid resize operations.

---

## Tabs in the Workbook

| Tab | Status | Notes |
|-----|--------|-------|
| Copy of Meta Feed_City | ✅ Done | 111,350 rows, production data |
| Copy of Meta Feed_Countries | ✅ Done | 2,400 rows, production data |
| Meta Feed_City | ⬇️ Shrunk to 1×1 | Original template, freed cells |
| Meta Feed_Countries | ⬇️ Shrunk to 1×1 | Original template, freed cells |
| Control Room | 📊 Source | 952 cities, read-only |
| geo_helper | ⚠️ 5.9M cells | Don't touch — huge but needed |
| PMax Feed | 📋 Template | Not yet generated |
| App Feed | 📋 Template | Not yet generated |

---

## Common Operations

### Re-run city feed
```bash
cd C:\Users\PabloGimeno\Documents\GitHub\Referral-Calculator
python meta_feed_city_generator.py
```

### Re-run country feed
```bash
cd C:\Users\PabloGimeno\Documents\GitHub\Referral-Calculator
python meta_feed_countries_generator.py
```

### Check cell usage
```bash
cd C:\Users\PabloGimeno
python check_cells.py
```

### Free cells (shrink unused tabs)
```bash
cd C:\Users\PabloGimeno
python free_cells.py
```

---

## Verification Checklist

After running any generator, verify:

1. **Row count**: Expected = (entities × languages × 50) + 1 header
   - City: 952 cities × avg ~2.34 langs × 50 = 111,350
   - Country: 22 countries × 48 total lang slots × ... wait, it's sum of langs per country × 50 = 2,400
2. **All 22 countries present** with correct language codes per URL Generator
3. **Formulas resolve** (Campaign name, Ad Set Name show computed values in Sheets)
4. **No trailing underscores** in Ad Set Name
5. **Column headers** all present even if data columns are empty
6. **Language column** has full names (English, not "en")
7. **Language code column** has codes (en, not "English")

---

## Math Breakdown

### Country Feed (2,400 rows)
```
BA(2) + ME(2) + MD(3) + BG(2) + HR(2) + UG(1) + RO(2) + RS(2) +
KE(2) + NG(1) + CI(2) + TN(3) + MA(2) + PT(2) + AM(3) + GE(2) +
PL(4) + KZ(3) + KG(2) + IT(2) + UA(2) + ES(2) = 48 language slots

48 × 50 rows = 2,400 rows
```

### City Feed (111,350 rows)
```
952 cities, each inherits its country's languages:
Sum across all cities of (languages_for_that_city's_country × 50)
= 111,350 rows
```

---

## Gotchas & Lessons Learned

1. **PowerShell + Python one-liners don't mix** — always write helper `.py` files instead
2. **10M cell limit is workbook-wide** — shrinking one tab frees cells for another
3. **`gspread` resize fails silently at 10M** — use `googleapiclient` directly
4. **Google Sheets CSV export caps at ~50K rows** — use API reads for verification
5. **`valueInputOption="USER_ENTERED"`** is required for formulas to work
6. **Row references in formulas must be calculated at generation time** — each row's formula points to its own row number
7. **Original tabs (Meta Feed_City, Meta Feed_Countries) were shrunk** to make room — don't re-expand them unless you shrink something else first
