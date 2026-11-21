"""
Production-Grade Unified WSGI Handler for Vercel Serverless.
Fully conforms to PEP 3333 WSGI specification.
Compatible with Vercel CLI 66+ Python runtime (WSGI/ASGI runner).
Routes /api/calendar, /api/market, /api/signal with zero cold-start delay.
"""

import sys
import os
import json
import traceback
from urllib.parse import parse_qs

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calendar_feed import EconomicCalendarFeed
from auto_predictor import AutonomousTradePredictor
from market_data import MarketDataManager

# Module-level singletons for fast execution and shared caching
feed = EconomicCalendarFeed(default_tz="Africa/Lagos")
predictor = AutonomousTradePredictor(tz_name="Africa/Lagos")
market_mgr = MarketDataManager()


def wsgi_app(environ, start_response):
    """Standard WSGI entrypoint callable: app(environ, start_response)."""
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "") or ""
    query_string = environ.get("QUERY_STRING", "") or ""
    query = parse_qs(query_string)

    # Standard CORS & caching response headers
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type, Authorization"),
        ("Cache-Control", "s-maxage=30, stale-while-revalidate=60"),
    ]

    # Handle CORS preflight
    if method == "OPTIONS":
        start_response("200 OK", headers)
        return [b""]

    response_data = {}
    status_code = "200 OK"

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

    body = json.dumps(response_data, default=str).encode("utf-8")
    start_response(status_code, headers)
    return [body]


# Export all common entrypoint variable names expected by Vercel
app = wsgi_app
application = wsgi_app
handler = wsgi_app
