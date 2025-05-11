
from flask import Flask, request, jsonify
from main import process_pdf_url

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "SmartOps GreaseGuardian Agent is live!"

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    if not data or "pdf_url" not in data:
        return jsonify({"error": "Missing 'pdf_url' in request"}), 400

    pdf_url = data["pdf_url"]
    try:
        result = process_pdf_url(pdf_url)
        return jsonify({"message": "Processing successful", "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
