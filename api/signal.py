"""
Vercel Serverless Function: /api/signal
WSGI callable compatible with Vercel Python runtime.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.index import app, application, handler
