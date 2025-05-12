from flask import Flask, request, jsonify
import requests
import fitz  # PyMuPDF
import re
import gspread
from google.oauth2.service_account import Credentials

# Init Flask
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "SmartOps GreaseGuardian Agent is Live ✅"

@app.route("/process", methods=["POST"])
def process():
    try:
        data = request.get_json()
        pdf_url = data.get("pdf_url")
        if not pdf_url:
            return jsonify({"error": "Missing 'pdf_url' in request"}), 400

        result = run_agent(pdf_url)
        return jsonify({"message": "Processing complete", "result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_agent(pdf_url):
    # Download PDF
    pdf_path = "daily_route.pdf"
    response = requests.get(pdf_url)
    with open(pdf_path, "wb") as f:
        f.write(response.content)

    print(f"✅ PDF downloaded to {pdf_path}")

    # Authenticate with Google Sheets
    creds = Credentials.from_service_account_file("smartopsbot-key.json")
    gc = gspread.authorize(creds)

    # Connect to the sheet
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1FzYbbqvc0Usc6s0Nse_sEaWgP3eVFNGX_uYi3D1jBY/edit?usp=sharing"
    sheet = gc.open_by_url(spreadsheet_url)
    worksheet = sheet.worksheet("May Daily")

    # Parse PDF
    doc = fitz.open(pdf_path)
    entries = []

    for page in doc:
        lines = page.get_text().split('\n')
        for i in range(2, len(lines)):
            line = lines[i]
            gallons_match = re.search(r"Total collected:\s*(\d+)\s*gal", line)
            name_match = re.search(r"Account:\s*(.+)", line)
            if gallons_match and name_match:
                gallons = int(gallons_match.group(1))
                name = name_match.group(1).strip()
                entries.append((name, gallons))

    # Update sheet
    for i in range(2, worksheet.row_count + 1):
        account = worksheet.cell(i, 1).value
        for name, gallons in entries:
            if name.lower() in account.lower():
                worksheet.update_cell(i, 5, gallons)
                break

    return f"{len(entries)} entries processed and updated."

if __name__ == "__main__":
    app.run(debug=False)