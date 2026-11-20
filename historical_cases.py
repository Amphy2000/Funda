"""
Historical Case Studies for High-Impact Economic Events on XAU/USD.
Contains documented real-world releases (CPI, NFP) with the exact numbers,
the initial market reaction, the 'second move', and the quantitative lesson.
"""

from typing import Dict, Any, List

HISTORICAL_CASES: List[Dict[str, Any]] = [
    {
        "id": "cpi_soft_2024_june",
        "title": "June 2024 CPI - The Textbook Disinflation Rally",
        "date": "June 12, 2024",
        "event_key": "CPI",
        "inputs": {
            "core_cpi_mom": {"actual": 0.16, "forecast": 0.30, "previous": 0.30},
            "headline_cpi_mom": {"actual": 0.00, "forecast": 0.10, "previous": 0.30},
            "core_cpi_yoy": {"actual": 3.4, "forecast": 3.5, "previous": 3.6},
            "headline_cpi_yoy": {"actual": 3.3, "forecast": 3.4, "previous": 3.4},
        },
        "initial_spike": "+$32.00 surge within 5 minutes ($2,315 -> $2,347)",
        "second_move": "Retraced to $2,336 (pullback), then expanded to $2,352 into London close.",
        "outcome": "Massive Bullish Run",
        "key_takeaway": (
            "All 4 inflation metrics missed to the downside simultaneously (zero conflict). "
            "10Y Treasury Yields tumbled 15 bps and DXY collapsed. "
            "This was the highest-conviction setup where buying the 15-minute pullback offered exceptional risk/reward."
        ),
    },
    {
        "id": "nfp_whip_2024_may",
        "title": "May 2024 NFP - The Classic Headline Beat Trap & Reversal",
        "date": "June 7, 2024",
        "event_key": "NFP",
        "inputs": {
            "headline_jobs": {"actual": 272.0, "forecast": 185.0, "previous": 165.0},
            "unemployment_rate": {"actual": 4.0, "forecast": 3.9, "previous": 3.9},
            "hourly_earnings_mom": {"actual": 0.40, "forecast": 0.30, "previous": 0.20},
            "hourly_earnings_yoy": {"actual": 4.10, "forecast": 3.90, "previous": 4.00},
        },
        "initial_spike": "Immediate -$45.00 plunge ($2,375 -> $2,330)",
        "second_move": "Consolidated around $2,330, attempted a small bounce to $2,342, then collapsed to $2,295 on PBOC gold-buying pause news.",
        "outcome": "Severe Bearish Trend",
        "key_takeaway": (
            "Headline jobs smashed expectations (+272k vs +185k) AND hourly wages accelerated (+0.4% vs +0.3%). "
            "Although the unemployment rate ticked up slightly to 4.0%, wage pressure and job additions completely dominated the Fed's calculus. "
            "Traders who attempted to buy the initial dip were wiped out."
        ),
    },
    {
        "id": "nfp_divergent_2023_dec",
        "title": "Conflicting NFP - The False Breakout Whipsaw",
        "date": "January 5, 2024",
        "event_key": "NFP",
        "inputs": {
            "headline_jobs": {"actual": 216.0, "forecast": 170.0, "previous": 173.0},
            "unemployment_rate": {"actual": 3.7, "forecast": 3.8, "previous": 3.7},
            "hourly_earnings_mom": {"actual": 0.40, "forecast": 0.30, "previous": 0.40},
            "hourly_earnings_yoy": {"actual": 4.10, "forecast": 3.90, "previous": 4.00},
        },
        "initial_spike": "Dipped $15 down to $2,024 on the headline beat, then skyrocketed $25 up to $2,049 within 30 minutes.",
        "second_move": "Complete V-shape reversal after ISM Services data 1.5 hours later came in disastrously weak at 50.6.",
        "outcome": "Two-Sided Liquidity Sweep",
        "key_takeaway": (
            "Never risk full size in the first 5 minutes of NFP. "
            "Even when NFP appears solid, subsequent morning data (like ISM at 10:00 AM ET) or underlying revisions can reverse the entire session."
        ),
    },
    {
        "id": "cpi_hot_2024_march",
        "title": "March 2024 CPI - Sticky Inflation Shock",
        "date": "April 10, 2024",
        "event_key": "CPI",
        "inputs": {
            "core_cpi_mom": {"actual": 0.36, "forecast": 0.30, "previous": 0.36},
            "headline_cpi_mom": {"actual": 0.38, "forecast": 0.30, "previous": 0.40},
            "core_cpi_yoy": {"actual": 3.8, "forecast": 3.7, "previous": 3.8},
            "headline_cpi_yoy": {"actual": 3.5, "forecast": 3.4, "previous": 3.2},
        },
        "initial_spike": "-$25 instant dump ($2,352 -> $2,327)",
        "second_move": "Rebounded back to $2,345 within 2 hours, then closed the week at fresh all-time highs of $2,400+.",
        "outcome": "Short-term Bearish, Long-term Structural Bullish",
        "key_takeaway": (
            "CRITICAL LESSON: Macro news affects the immediate 1-to-4 hour horizon. "
            "However, during strong secular bull markets driven by geopolitical tensions and central bank accumulation, "
            "Gold treats hot CPI dips as buying opportunities after the initial drop exhausts itself."
        ),
    },
]
