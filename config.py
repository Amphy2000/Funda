"""
Configuration for XAU/USD Macro & News Directional Predictor.
Defines economic indicators, component weights, expected standard deviations (for Z-score calculation),
and correlation baselines with Gold (XAU/USD).
"""

from typing import Dict, Any

# Historical standard deviations of consensus surprise (Actual - Forecast)
# Used to compute Z-score: (Actual - Forecast) / STD_DEV
EVENT_SPECS: Dict[str, Dict[str, Any]] = {
    "NFP": {
        "title": "US Employment Situation (NFP)",
        "frequency": "Monthly (First Friday)",
        "source": "Bureau of Labor Statistics (BLS)",
        "description": "Measures change in non-farm payrolls, unemployment rate, and hourly wage growth.",
        "components": {
            "headline_jobs": {
                "label": "Non-Farm Payrolls (k)",
                "unit": "k",
                "std_dev": 45.0,  # Average surprise deviation in thousands
                "weight": 0.40,
                "gold_impact": -1,  # + Jobs -> + USD/Yields -> - Gold (Bearish)
                "threshold_significant": 35.0,
            },
            "unemployment_rate": {
                "label": "Unemployment Rate (%)",
                "unit": "%",
                "std_dev": 0.15,
                "weight": 0.25,
                "gold_impact": 1,  # + Unemployment -> - USD/Yields -> + Gold (Bullish)
                "threshold_significant": 0.10,
            },
            "hourly_earnings_mom": {
                "label": "Avg Hourly Earnings MoM (%)",
                "unit": "%",
                "std_dev": 0.10,
                "weight": 0.25,
                "gold_impact": -1,  # + Wage inflation -> Hawkish Fed -> - Gold (Bearish)
                "threshold_significant": 0.10,
            },
            "hourly_earnings_yoy": {
                "label": "Avg Hourly Earnings YoY (%)",
                "unit": "%",
                "std_dev": 0.15,
                "weight": 0.10,
                "gold_impact": -1,
                "threshold_significant": 0.10,
            },
        },
    },
    "CPI": {
        "title": "Consumer Price Index (CPI)",
        "frequency": "Monthly (~Middle of month)",
        "source": "Bureau of Labor Statistics (BLS)",
        "description": "Primary gauge of retail inflation. Core MoM is heavily scrutinized by the Fed.",
        "components": {
            "core_cpi_mom": {
                "label": "Core CPI MoM (%)",
                "unit": "%",
                "std_dev": 0.08,
                "weight": 0.45,
                "gold_impact": -1,  # Hot Core -> Hawkish Fed / High Yields -> - Gold
                "threshold_significant": 0.05,
            },
            "headline_cpi_mom": {
                "label": "Headline CPI MoM (%)",
                "unit": "%",
                "std_dev": 0.10,
                "weight": 0.25,
                "gold_impact": -1,
                "threshold_significant": 0.10,
            },
            "core_cpi_yoy": {
                "label": "Core CPI YoY (%)",
                "unit": "%",
                "std_dev": 0.12,
                "weight": 0.20,
                "gold_impact": -1,
                "threshold_significant": 0.10,
            },
            "headline_cpi_yoy": {
                "label": "Headline CPI YoY (%)",
                "unit": "%",
                "std_dev": 0.15,
                "weight": 0.10,
                "gold_impact": -1,
                "threshold_significant": 0.10,
            },
        },
    },
    "PPI": {
        "title": "Producer Price Index (PPI)",
        "frequency": "Monthly",
        "source": "Bureau of Labor Statistics (BLS)",
        "description": "Wholesale pipeline inflation. Precedes and influences PCE/CPI.",
        "components": {
            "core_ppi_mom": {
                "label": "Core PPI MoM (%)",
                "unit": "%",
                "std_dev": 0.15,
                "weight": 0.50,
                "gold_impact": -1,
                "threshold_significant": 0.10,
            },
            "headline_ppi_mom": {
                "label": "Headline PPI MoM (%)",
                "unit": "%",
                "std_dev": 0.20,
                "weight": 0.30,
                "gold_impact": -1,
                "threshold_significant": 0.15,
            },
            "core_ppi_yoy": {
                "label": "Core PPI YoY (%)",
                "unit": "%",
                "std_dev": 0.25,
                "weight": 0.20,
                "gold_impact": -1,
                "threshold_significant": 0.20,
            },
        },
    },
    "RETAIL_SALES": {
        "title": "US Retail Sales",
        "frequency": "Monthly",
        "source": "US Census Bureau",
        "description": "Consumer spending health. Robust spending indicates resilient demand and delayed rate cuts.",
        "components": {
            "core_retail_sales_mom": {
                "label": "Core Retail Sales MoM (%)",
                "unit": "%",
                "std_dev": 0.25,
                "weight": 0.60,
                "gold_impact": -1,
                "threshold_significant": 0.20,
            },
            "headline_retail_sales_mom": {
                "label": "Headline Retail Sales MoM (%)",
                "unit": "%",
                "std_dev": 0.30,
                "weight": 0.40,
                "gold_impact": -1,
                "threshold_significant": 0.25,
            },
        },
    },
}

# Tickers used for intermarket correlation analysis
INTERMARKET_TICKERS = {
    "GOLD": "GC=F",          # COMEX Gold Futures (proxy for XAU/USD)
    "DXY": "DX-Y.NYB",       # US Dollar Index
    "DXY_ALT": "UUP",        # Invesco DB US Dollar Bullish Fund (backup if DXY fails)
    "US10Y": "^TNX",         # 10-Year US Treasury Yield (10x basis points)
    "US05Y": "^FVX",         # 5-Year US Treasury Yield
    "TIPS": "TIP",           # iShares TIPS Bond ETF (inverse real yields)
}

# Execution Timeframes & Guidance
EXECUTION_PHASES = {
    "PHASE_1": {
        "timeframe": "0 - 5 Minutes Post-News",
        "name": "Volatility Vacuum / No-Trade Zone",
        "action": "STAND ASIDE / DO NOT MARKET ORDER",
        "reason": "Institutional latency dominance, spread expansion (up to $5+), order book liquidity vacuum, high slippage.",
    },
    "PHASE_2": {
        "timeframe": "5 - 15 Minutes Post-News",
        "name": "Price Discovery & Absorption",
        "action": "MONITOR M5 CANDLE RANGE",
        "reason": "Identify the high/low range of the impulse candle. Watch whether price respects macro bias or rejects it.",
    },
    "PHASE_3": {
        "timeframe": "15 - 60 Minutes Post-News",
        "name": "Second Move / Institutional Participation",
        "action": "TRADE WITH BIAS ON RETRACEMENT",
        "reason": "Enter only if price breaks M5/M15 news structure in the direction of the confirmed macro surprise with defined risk.",
    },
}
