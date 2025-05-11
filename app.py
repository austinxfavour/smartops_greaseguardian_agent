from flask import Flask, request, jsonify
from main import process_pdf_url

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

        result = process_pdf_url(pdf_url)
        return jsonify({"message": "Processing complete", "result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False)