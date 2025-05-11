from flask import Flask, request, jsonify
import main

app = Flask(__name__)

@app.route("/", methods=["POST"])
def handle_webhook():
    try:
        data = request.get_json()
        pdf_url = data.get("pdf_url")
        if not pdf_url:
            return jsonify({"error": "No PDF URL provided"}), 400

        result = main.run_agent(pdf_url)
        return jsonify({"status": "success", "message": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return "SmartOps Agent is live!", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)