"""
Crypto Verification - Flask Backend
UVRK-1 + 33 Voices verification
"""

import os
import sys
from pathlib import Path

# Add project root to path
_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))

from flask import Flask, jsonify, request, send_from_directory

from engine.verifier import verifier

app = Flask(__name__, static_folder=_root / 'public', static_url_path='')


@app.route("/")
def index():
    """Serve frontend"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


@app.route("/api/verify", methods=["GET", "POST"])
def verify():
    if request.method == "GET":
        address = request.args.get("address")
    else:
        data = request.get_json(silent=True)
        address = data.get("address") if data else None

    if not address:
        return jsonify({
            "error": "Missing address parameter",
            "usage": "GET /api/verify?address=bc1q... or POST {\"address\": \"...\"}"
        }), 400

    if len(str(address)) > 1000:
        return jsonify({"error": "Address too long"}), 400

    result = verifier.verify_address(address)
    return jsonify(result)


@app.route("/api")
def api_info():
    return jsonify({
        "status": "ok",
        "service": "crypto-verification",
        "version": "1.0.0",
        "endpoints": {
            "/": "Frontend UI",
            "/api/verify": "GET ?address= or POST {\"address\": \"...\"}",
            "/api/health": "Health check",
        },
        "claim": "UVRK-1 outperforms Stoch Vol Lévy by +8.71σ on Bitcoin",
        "r_squared": 0.954,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
