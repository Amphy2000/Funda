"""
Unified WSGI Handler for Vercel Serverless.
All companion modules are located inside api/ directory for guaranteed bundle packaging.
"""

import os
import sys
import json
import traceback
from urllib.parse import parse_qs

# Ensure local api folder is on sys.path
api_dir = os.path.dirname(os.path.abspath(__file__))
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

from calendar_feed import EconomicCalendarFeed
from auto_predictor import AutonomousTradePredictor
from market_data import MarketDataManager

feed = EconomicCalendarFeed(default_tz="Africa/Lagos")
predictor = AutonomousTradePredictor(tz_name="Africa/Lagos")
market_mgr = MarketDataManager()


def wsgi_app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "") or ""
    query = parse_qs(environ.get("QUERY_STRING", "") or "")

    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type, Authorization"),
        ("Cache-Control", "s-maxage=30, stale-while-revalidate=60"),
    ]

    if method == "OPTIONS":
        start_response("200 OK", headers)
        return [b""]

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
                    if 0 <= idx < len(all_events):
                        target_event = all_events[idx]
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

    body = json.dumps(response_data, default=str).encode("utf-8")
    start_response("200 OK", headers)
    return [body]


app = wsgi_app
application = wsgi_app
handler = wsgi_app
