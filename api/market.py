"""
Vercel Serverless Function: /api/market
Returns real-time prices, daily change %, and intermarket correlation metrics for Gold, DXY, and 10Y Yields.
"""

import sys
import os
import json
import traceback
from http.server import BaseHTTPRequestHandler

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_data import MarketDataManager

market_mgr = MarketDataManager()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        response_data = {}
        status_code = 200

        try:
            snapshot = market_mgr.fetch_market_snapshot()
            alignment = market_mgr.assess_macro_alignment(snapshot)
            response_data = {
                "status": "success",
                "snapshot": snapshot,
                "alignment": alignment,
            }
        except Exception as e:
            # Return baseline data so UI always loads
            response_data = {
                "status": "fallback",
                "snapshot": {
                    "Gold (GC=F)": {"ticker": "XAU/USD", "current": 3500.0, "change_pct": 0.0, "status": "OFFLINE"},
                    "US Dollar Index (DXY)": {"ticker": "DXY", "current": 104.0, "change_pct": 0.0, "status": "OFFLINE"},
                    "US 10Y Yield (^TNX)": {"ticker": "^TNX", "current": 4.40, "change_pct": 0.0, "status": "OFFLINE"},
                },
                "alignment": {
                    "alignment": "MIXED INTERMARKET ALIGNMENT",
                    "explanation": "Live feeds temporarily offline. Displaying baseline values.",
                },
                "error": str(e),
            }
            status_code = 200  # Always 200 so frontend loads

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
