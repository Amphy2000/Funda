"""
Vercel Serverless Function: /api/market
Returns real-time prices, daily change %, and intermarket correlation metrics for Gold, DXY, and 10Y Yields.
"""

import sys
import os
import json
from http.server import BaseHTTPRequestHandler

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_data import MarketDataManager

market_mgr = MarketDataManager()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            snapshot = market_mgr.fetch_market_snapshot()
            alignment = market_mgr.assess_macro_alignment(snapshot)
            response_data = {
                "status": "success",
                "snapshot": snapshot,
                "alignment": alignment,
            }
            status_code = 200
        except Exception as e:
            response_data = {
                "status": "error",
                "message": str(e),
                "snapshot": {},
                "alignment": {"alignment": "NEUTRAL", "explanation": "Feed initializing"},
            }
            status_code = 500

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Cache-Control", "s-maxage=30, stale-while-revalidate=60")
        self.end_headers()

        self.wfile.write(json.dumps(response_data, default=str).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
