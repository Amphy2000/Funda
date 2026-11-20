"""
Production-Grade Unified Vercel Serverless Handler.
Routes /api/calendar, /api/signal, /api/market, and /api/health with zero latency.
Features defensive error catching and fast in-memory execution.
"""

import sys
import os
import json
import traceback
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calendar_feed import EconomicCalendarFeed
from auto_predictor import AutonomousTradePredictor
from market_data import MarketDataManager

# Single global instances to enable in-memory cache reuse across requests
feed = EconomicCalendarFeed(default_tz="Africa/Lagos")
predictor = AutonomousTradePredictor(tz_name="Africa/Lagos")
market_mgr = MarketDataManager()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "s-maxage=30, stale-while-revalidate=60")
        self.end_headers()

        response_data = {}

        try:
            if "calendar" in path:
                period = query.get("period", ["all"])[0]
                events = feed.fetch_events(period_filter=period, impact_filter=["High", "Medium"])
                response_data = {
                    "status": "success",
                    "period": period,
                    "timezone": "West Central Africa Time (WAT / UTC+1)",
                    "count": len(events),
                    "events": events,
                }

            elif "signal" in path:
                event_idx_str = query.get("event_index", [None])[0]
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

                signal_data = predictor.generate_automated_signal(event_override=target_event)
                response_data = {
                    "status": "success",
                    "timezone": "West Central Africa Time (WAT / UTC+1)",
                    "signal": signal_data,
                }

            elif "market" in path:
                snapshot = market_mgr.fetch_market_snapshot()
                alignment = market_mgr.assess_macro_alignment(snapshot)
                response_data = {
                    "status": "success",
                    "snapshot": snapshot,
                    "alignment": alignment,
                }

            else:
                response_data = {
                    "status": "online",
                    "service": "Gold Pulse AI Vercel API",
                    "endpoints": ["/api/calendar", "/api/signal", "/api/market"],
                }

        except Exception as e:
            response_data = {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc(),
            }

        self.wfile.write(json.dumps(response_data, default=str).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
