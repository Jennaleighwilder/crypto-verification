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

import logging
from flask import Flask, jsonify, request, send_from_directory

from engine.verifier import verifier

logger = logging.getLogger(__name__)

try:
    from engine.ramanash_kernel import MACRO_FEB_23_2026
    RAMANASH_AVAILABLE = True
except ImportError:
    MACRO_FEB_23_2026 = None
    RAMANASH_AVAILABLE = False

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
        macro_factors = None
    else:
        data = request.get_json(silent=True)
        address = data.get("address") if data else None
        macro_factors = data.get("macro_factors") if data else None

    if not address:
        return jsonify({
            "error": "Missing address parameter",
            "usage": "GET /api/verify?address=bc1q... or POST {\"address\": \"...\", \"macro_factors\": {...}}"
        }), 400

    if len(str(address)) > 1000:
        return jsonify({"error": "Address too long"}), 400

    if macro_factors is None and RAMANASH_AVAILABLE:
        macro_factors = MACRO_FEB_23_2026
        logger.info("[AUTO-MACRO] Using MACRO_FEB_23_2026")

    result = verifier.verify_address(address, macro_factors=macro_factors)
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
