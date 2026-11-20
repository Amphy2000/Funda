"""
Intermarket Market Data Module.
Fetches real-time and historical data for Gold (GC=F), US Dollar Index (DX-Y.NYB),
US 10-Year Treasury Yield (^TNX), and TIPS (TIP) using yfinance.
Calculates rolling correlations and intermarket macro alignment.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import yfinance as yf
from config import INTERMARKET_TICKERS


class MarketDataManager:
    """Manages fetching and analyzing real-time intermarket correlations."""

    def __init__(self):
        self.tickers = INTERMARKET_TICKERS

    def fetch_market_snapshot(self) -> Dict[str, Any]:
        """
        Fetches the latest prices and daily percentage changes for the key macro assets.
        """
        results = {}
        assets = [
            ("Gold (GC=F)", self.tickers["GOLD"]),
            ("US Dollar Index (DXY)", self.tickers["DXY"]),
            ("US 10Y Yield (^TNX)", self.tickers["US10Y"]),
            ("US TIPS (TIP)", self.tickers["TIPS"]),
        ]

        for name, ticker in assets:
            try:
                t = yf.Ticker(ticker)
                # Fetch recent 5 days to ensure we have the last two trading sessions
                hist = t.history(period="5d", interval="1d")
                if hist.empty and ticker == self.tickers["DXY"]:
                    # Fallback to UUP ETF if DXY is not accessible
                    t = yf.Ticker(self.tickers["DXY_ALT"])
                    hist = t.history(period="5d", interval="1d")
                    name = "US Dollar Bullish (UUP)"

                if not hist.empty and len(hist) >= 2:
                    current = float(hist["Close"].iloc[-1])
                    previous = float(hist["Close"].iloc[-2])
                    change_pct = ((current - previous) / previous) * 100.0
                    results[name] = {
                        "ticker": ticker,
                        "current": round(current, 2 if "Yield" not in name else 3),
                        "previous": round(previous, 2 if "Yield" not in name else 3),
                        "change_pct": round(change_pct, 2),
                        "status": "ONLINE",
                    }
                elif not hist.empty:
                    current = float(hist["Close"].iloc[-1])
                    results[name] = {
                        "ticker": ticker,
                        "current": round(current, 2),
                        "previous": round(current, 2),
                        "change_pct": 0.0,
                        "status": "ONLINE",
                    }
                else:
                    results[name] = {"status": "NO_DATA", "current": None, "change_pct": 0.0}
            except Exception as e:
                results[name] = {"status": "ERROR", "error": str(e), "current": None, "change_pct": 0.0}

        return results

    def fetch_historical_series(self, period: str = "3mo") -> pd.DataFrame:
        """
        Fetches aligned daily closing prices for correlation calculation.
        """
        ticker_list = [self.tickers["GOLD"], self.tickers["US10Y"], self.tickers["DXY"], self.tickers["TIPS"]]
        try:
            raw_data = yf.download(
                tickers=ticker_list,
                period=period,
                interval="1d",
                progress=False,
                auto_adjust=True,
            )
            if raw_data.empty:
                return pd.DataFrame()

            close_df = raw_data["Close"].copy()
            # Rename columns to friendly names
            col_map = {
                self.tickers["GOLD"]: "Gold",
                self.tickers["US10Y"]: "US 10Y Yield",
                self.tickers["DXY"]: "DXY",
                self.tickers["TIPS"]: "TIPS ETF",
            }
            close_df = close_df.rename(columns=col_map)
            # Forward-fill and drop remaining NAs
            close_df = close_df.ffill().dropna()
            return close_df
        except Exception:
            return pd.DataFrame()

    def calculate_correlations(self, period: str = "3mo") -> Dict[str, Any]:
        """
        Calculates correlation of returns between Gold and other macro assets.
        """
        df = self.fetch_historical_series(period=period)
        if df.empty or len(df) < 5:
            # Return standard theoretical baselines if market data is unavailable
            return {
                "gold_vs_dxy": -0.75,
                "gold_vs_yield": -0.68,
                "gold_vs_tips": 0.72,
                "period": period,
                "status": "FALLBACK_BASELINE",
            }

        pct_changes = df.pct_change().dropna()
        corr_matrix = pct_changes.corr()

        gold_vs_dxy = corr_matrix.loc["Gold", "DXY"] if "DXY" in corr_matrix.columns else -0.75
        gold_vs_yield = corr_matrix.loc["Gold", "US 10Y Yield"] if "US 10Y Yield" in corr_matrix.columns else -0.68
        gold_vs_tips = corr_matrix.loc["Gold", "TIPS ETF"] if "TIPS ETF" in corr_matrix.columns else 0.72

        return {
            "gold_vs_dxy": round(float(gold_vs_dxy), 2),
            "gold_vs_yield": round(float(gold_vs_yield), 2),
            "gold_vs_tips": round(float(gold_vs_tips), 2),
            "period": period,
            "status": "CALCULATED",
        }

    def assess_macro_alignment(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compares today's moves across Gold, DXY, and 10Y Yields to see if macro dynamics
        support Gold bulls, Gold bears, or show market divergence.
        """
        gold_data = snapshot.get("Gold (GC=F)", {})
        dxy_data = snapshot.get("US Dollar Index (DXY)") or snapshot.get("US Dollar Bullish (UUP)", {})
        yield_data = snapshot.get("US 10Y Yield (^TNX)", {})

        gold_chg = gold_data.get("change_pct", 0.0)
        dxy_chg = dxy_data.get("change_pct", 0.0)
        yield_chg = yield_data.get("change_pct", 0.0)

        # Macro Alignment Evaluation
        # Normal alignment: Yields and DXY down -> Gold Bullish
        # Normal alignment: Yields and DXY up -> Gold Bearish
        # Divergent alignment: Yields up but Gold up -> Strong physical bid / Geopolitics / De-dollarization
        alignment = "NEUTRAL"
        explanation = ""

        if yield_chg > 0.5 and dxy_chg > 0.2:
            if gold_chg < -0.3:
                alignment = "STRONG MACRO HEADWIND (BEARISH CONFIRMED)"
                explanation = "Higher yields and a firmer US Dollar are exerting textbook fundamental pressure on Gold."
            else:
                alignment = "MACRO DIVERGENCE (GOLD RESILIENCE)"
                explanation = "Yields and USD are rising, yet Gold is holding firm. This indicates strong underlying physical, central bank, or safe-haven demand overriding rate yields."
        elif yield_chg < -0.5 and dxy_chg < -0.2:
            if gold_chg > 0.3:
                alignment = "STRONG MACRO TAILWIND (BULLISH CONFIRMED)"
                explanation = "Declining yields and a soft Dollar provide ideal conditions for Gold appreciation."
            else:
                alignment = "MACRO DIVERGENCE (GOLD LAGGING)"
                explanation = "Yields and USD are weakening, but Gold has failed to capitalize. Inspect equity market liquidity or profit-taking."
        else:
            alignment = "MIXED / CONSOLIDATION"
            explanation = "Intermarket yields and currency fluctuations are within normal daily noise."

        return {
            "alignment": alignment,
            "explanation": explanation,
            "gold_change": gold_chg,
            "dxy_change": dxy_chg,
            "yield_change": yield_chg,
        }
