import requests
import fitz  # PyMuPDF
import re
import gspread
from google.oauth2.service_account import Credentials

def run_agent(pdf_url):
    # Download the PDF from the provided URL
    pdf_path = "daily_route.pdf"
    response = requests.get(pdf_url)
    with open(pdf_path, "wb") as f:
        f.write(response.content)

    print(f"✅ PDF downloaded to {pdf_path}")

    # Authenticate with Google Sheets
    creds = Credentials.from_service_account_file("smartopsbot-key.json")
    gc = gspread.authorize(creds)

    # Connect to the KPI sheet
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1FzYbbqvC0usc6soNse_sEaWgP3eVFNGX_uYid3IjBY/edit?usp=sharing'
    sheet = gc.open_by_url(spreadsheet_url)
    worksheet = sheet.worksheet("May Daily")

    # Extract gallons + accounts from PDF
    doc = fitz.open(pdf_path)
    entries = []

    for page in doc:
        lines = page.get_text().split('\n')
        for i in range(2, len(lines)):
            line = lines[i]
            gallons_match = re.search(r"Total collected:\s*(\d+)\s*gal", line)
            if gallons_match:
                gallons = gallons_match.group(1).strip()
                account_line = re.sub(r"^\d+\s+", "", lines[i - 3]).strip()
                if len(account_line) > 2 and not account_line.lower().startswith("entry info"):
                    entries.append({
                        "account": account_line,
                        "gallons": gallons
                    })

    # Update the sheet
    all_rows = worksheet.get_all_values()
    ACCOUNT_COL = 1  # B
    ACTUAL_COL = 4   # E
    updated = 0

    for entry in entries:
        raw_account = entry["account"]
        account_name = raw_account.strip().lower()
        gallons = entry["gallons"]
        for idx, row in enumerate(all_rows):
            if idx == 0:
                continue
            sheet_account = row[ACCOUNT_COL].strip().lower()
            if sheet_account == account_name:
                cell = gspread.utils.rowcol_to_a1(idx + 1, ACTUAL_COL + 1)
                worksheet.update(cell, [[gallons]])
                updated += 1
                print(f"✅ Updated {raw_account} → {gallons} gal at {cell}")
                break

    return f"{updated} rows updated from PDF"