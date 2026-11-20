"""
Vercel Serverless Function: /api/signal
Generates autonomous macro trade signal for XAU/USD.
Accepts optional ?event_index=N to target specific calendar events.
"""

import sys
import os
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calendar_feed import EconomicCalendarFeed
from auto_predictor import AutonomousTradePredictor

predictor = AutonomousTradePredictor(tz_name="Africa/Lagos")
feed = EconomicCalendarFeed(default_tz="Africa/Lagos")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        event_idx_str = query_params.get("event_index", [None])[0]

        target_event = None
        if event_idx_str is not None:
            try:
                idx = int(event_idx_str)
                all_events = feed.fetch_events(period_filter="all", impact_filter=["High", "Medium"])
                high_events = [e for e in all_events if e.get("impact") == "High"]
                event_pool = high_events if high_events else all_events
                if 0 <= idx < len(event_pool):
                    target_event = event_pool[idx]
            except Exception:
                target_event = None

        try:
            signal_data = predictor.generate_automated_signal(event_override=target_event)
            response_data = {
                "status": "success",
                "timezone": "West Central Africa Time (WAT / UTC+1)",
                "signal": signal_data,
            }
            status_code = 200
        except Exception as e:
            response_data = {
                "status": "error",
                "message": str(e),
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
