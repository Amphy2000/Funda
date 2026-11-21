"""
Vercel Serverless Function: /api/calendar
Returns live economic calendar events localized to West Central Africa Time (WAT).
Supports ?period=all, ?period=this_week, ?period=next_week
"""

import sys
import os
import json
import traceback
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Ensure root directory is on sys.path for local & Vercel serverless execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calendar_feed import EconomicCalendarFeed

feed = EconomicCalendarFeed(default_tz="Africa/Lagos")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse query params
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        period = query_params.get("period", ["all"])[0]

        response_data = {}
        status_code = 200

        try:
            events = feed.fetch_events(period_filter=period, impact_filter=["High", "Medium"])
            response_data = {
                "status": "success",
                "period": period,
                "timezone": "West Central Africa Time (WAT / UTC+1)",
                "count": len(events),
                "events": events,
            }
        except Exception as e:
            # Safe fallback - combine both week fallbacks
            try:
                fallback = feed._get_fallback_this_week() + feed._get_fallback_next_week()
            except Exception:
                fallback = []
            response_data = {
                "status": "fallback",
                "period": period,
                "timezone": "West Central Africa Time (WAT / UTC+1)",
                "count": len(fallback),
                "events": fallback,
                "error": str(e),
            }
            status_code = 200  # Return 200 with fallback data so UI still loads

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Cache-Control", "s-maxage=60, stale-while-revalidate=120")
        self.end_headers()

        self.wfile.write(json.dumps(response_data, default=str).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
