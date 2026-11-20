"""
Unified Vercel Serverless Entrypoint.
Routes incoming /api/calendar, /api/signal, and /api/market requests.
"""

import sys
import os
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.calendar import handler as CalendarHandler
from api.signal import handler as SignalHandler
from api.market import handler as MarketHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if "calendar" in path:
            CalendarHandler.do_GET(self)
        elif "signal" in path:
            SignalHandler.do_GET(self)
        elif "market" in path:
            MarketHandler.do_GET(self)
        else:
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            data = {
                "status": "online",
                "service": "Gold Pulse AI Vercel API",
                "endpoints": ["/api/calendar", "/api/signal", "/api/market"],
            }
            self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
