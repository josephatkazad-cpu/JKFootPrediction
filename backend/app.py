import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from services.sportmonks import SportMonksClient
from services.analysis import analyze_match

load_dotenv()

app = Flask(__name__)
CORS(app)

client = SportMonksClient(os.getenv("SPORTMONKS_TOKEN", ""))

@app.get("/")
def home():
    return jsonify({"ok": True, "app": "JK Prédiction", "version": "1.0.0"})

@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "tokenConfigured": bool(os.getenv("SPORTMONKS_TOKEN")),
        "app": "JK Prédiction"
    })

@app.get("/api/fixtures")
def fixtures():
    date = request.args.get("date")
    try:
        return jsonify(client.fixtures_by_date(date))
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 502

@app.get("/api/analyze/<int:fixture_id>")
def analyze(fixture_id):
    try:
        match = client.fixture_details(fixture_id)
        result = analyze_match(client, match)
        return jsonify({"ok": True, "fixture": fixture_id, "analysis": result})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
