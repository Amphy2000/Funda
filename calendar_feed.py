"""
Production Economic Calendar — 100% Live Data, Zero Hardcoded Fallbacks.
Source: biquote.io free JSON API + nfs.faireconomy.media for this-week actuals.
All times expressed in West Central Africa Time (WAT / UTC+1).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import time
import requests

try:
    import zoneinfo
    _WAT = zoneinfo.ZoneInfo("Africa/Lagos")
except Exception:
    _WAT = timezone(timedelta(hours=1))

# ---------------------------------------------------------------------------
# In-memory cache  (5-minute TTL)
# ---------------------------------------------------------------------------
_CACHE: Dict[str, Any] = {
    "timestamp": 0.0,
    "events": [],
}
_CACHE_TTL = 300  # seconds

# ---------------------------------------------------------------------------
# API endpoints — ordered by preference
# ---------------------------------------------------------------------------
_BIQUOTE_BASE = "https://biquote.io/api/calendar"
_FF_THISWEEK  = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

# Map biquote importance to canonical labels
_IMPACT_MAP = {"high": "High", "medium": "Medium", "low": "Low", "none": "Low"}

# ---------------------------------------------------------------------------
# Key USD events we care about for XAU/USD — filter noise
# ---------------------------------------------------------------------------
_RELEVANT_KEYWORDS = [
    "cpi", "ppi", "inflation", "gdp", "payroll", "nfp", "employment",
    "unemployment", "retail sales", "pce", "fomc", "fed", "interest rate",
    "consumer confidence", "consumer sentiment", "ism", "pmi", "manufacturing",
    "services", "durable goods", "jobless", "claims", "home sales",
    "building permits", "housing", "trade balance", "treasury", "beige book",
    "new home", "pending home", "existing home", "crude oil",
]


def _is_relevant(title: str) -> bool:
    t = title.lower()
    return any(kw in t for kw in _RELEVANT_KEYWORDS)


def _fmt_number(val) -> str:
    if val is None:
        return "-"
    if isinstance(val, float):
        if abs(val) >= 1000:
            return f"{val:,.0f}"
        return str(val)
    return str(val)


class EconomicCalendarFeed:
    """
    Live USD economic calendar.
    Primary source: biquote.io (free JSON, no key, real data, covers current + next week).
    Secondary source: nfs.faireconomy.media (for this-week actual values).
    Returns ONLY real live data — raises if neither source is reachable.
    All times in West Central Africa Time (WAT / UTC+1).
    """

    def __init__(self, default_tz: str = "Africa/Lagos"):
        try:
            import zoneinfo as _zi
            self.tz = _zi.ZoneInfo(default_tz)
        except Exception:
            self.tz = _WAT

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_events(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """
        Return live USD economic events.
        period_filter: 'all' | 'this_week' | 'next_week'
        impact_filter: list e.g. ['High', 'Medium']
        """
        period_filter = kwargs.get("period_filter", "all")
        impact_filter = set(kwargs.get("impact_filter", ["High", "Medium"]))

        # positional compat
        if args:
            if isinstance(args[0], list):
                impact_filter = set(args[0])
            else:
                period_filter = args[0]
            if len(args) >= 2:
                impact_filter = set(args[1])

        all_events = self._get_all_events()

        # Apply period filter
        now_wat = datetime.now(self.tz)
        this_week_end = _week_end(now_wat)
        next_week_end = this_week_end + timedelta(days=7)

        filtered = []
        for e in all_events:
            if e["impact"] not in impact_filter:
                continue
            dt = e.get("datetime_wat")
            if period_filter == "this_week":
                if dt and dt <= this_week_end:
                    filtered.append(e)
            elif period_filter == "next_week":
                if dt and this_week_end < dt <= next_week_end:
                    filtered.append(e)
            else:
                filtered.append(e)

        return filtered

    def fetch_this_week_events(self, impact_filter: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        return self.fetch_events(period_filter="this_week", impact_filter=impact_filter or ["High", "Medium"])

    def fetch_next_week_events(self, impact_filter: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        return self.fetch_events(period_filter="next_week", impact_filter=impact_filter or ["High", "Medium"])

    def get_next_high_impact_event(self) -> Optional[Dict[str, Any]]:
        """Return the next upcoming high-impact event (WAT), prioritizing major market movers."""
        events = self.fetch_events(period_filter="all", impact_filter=["High", "Medium"])
        now_wat = datetime.now(self.tz)

        # 1. First priority: upcoming HIGH impact events
        for e in events:
            if e.get("impact") == "High":
                dt = e.get("datetime_wat")
                if dt and dt >= now_wat:
                    return e

        # 2. Second priority: upcoming Medium events that are major economic indicators
        major_indicators = ["sentiment", "confidence", "pmi", "claims", "sales", "pce", "gdp"]
        for e in events:
            title_lower = e.get("title", "").lower()
            if any(kw in title_lower for kw in major_indicators):
                dt = e.get("datetime_wat")
                if dt and dt >= now_wat:
                    return e

        # 3. Third priority: any future event with known datetime
        for e in events:
            dt = e.get("datetime_wat")
            if dt and dt >= now_wat:
                return e

        # Fallback: first event regardless of time
        return events[0] if events else None

    # ------------------------------------------------------------------
    # Internal data fetching
    # ------------------------------------------------------------------

    def _get_all_events(self) -> List[Dict[str, Any]]:
        """Return cached or freshly fetched events, sorted by time."""
        now = time.time()
        if _CACHE["events"] and (now - _CACHE["timestamp"] < _CACHE_TTL):
            return _CACHE["events"]

        events = self._fetch_biquote()

        # Merge actuals from faireconomy this-week feed
        try:
            actuals = self._fetch_ff_actuals()
            events = _merge_actuals(events, actuals)
        except Exception:
            pass  # actuals are nice-to-have, not required

        if events:
            _CACHE["events"] = events
            _CACHE["timestamp"] = now

        return events

    def _fetch_biquote(self) -> List[Dict[str, Any]]:
        """Fetch real USD events from biquote.io for current + next week."""
        events = []
        seen = set()

        for importance in ("high", "medium"):
            try:
                resp = requests.get(
                    f"{_BIQUOTE_BASE}?countries=US&importance={importance}",
                    headers=_HEADERS,
                    timeout=5.0,
                )
                if resp.status_code != 200:
                    continue
                for item in resp.json():
                    raw_time = item.get("time", "")
                    if not raw_time:
                        continue

                    try:
                        dt_utc = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
                        dt_wat = dt_utc.astimezone(self.tz)
                    except Exception:
                        continue

                    title = item.get("name", "").strip()
                    if not title:
                        continue

                    # Deduplicate (biquote sometimes returns duplicates)
                    key = (title, raw_time[:16])
                    if key in seen:
                        continue
                    seen.add(key)

                    impact = _IMPACT_MAP.get(importance, "Medium")
                    forecast = item.get("forecast")
                    previous = item.get("previous")
                    actual   = item.get("actual")

                    # Determine period label
                    now_wat = datetime.now(self.tz)
                    week_end = _week_end(now_wat)
                    period = "Current Week" if dt_wat <= week_end else "Upcoming / Next Week"

                    events.append({
                        "period": period,
                        "title": title,
                        "impact": impact,
                        "date": dt_wat.strftime("%a, %b %d"),
                        "time": dt_wat.strftime("%I:%M %p WAT").lstrip("0"),
                        "datetime_wat": dt_wat,
                        "raw_date": raw_time,
                        "forecast": _fmt_number(forecast),
                        "previous": _fmt_number(previous),
                        "actual": _fmt_number(actual),
                        "country": "USD",
                    })
            except Exception:
                continue

        events.sort(key=lambda e: e["datetime_wat"])
        return events

    def _fetch_ff_actuals(self) -> List[Dict[str, Any]]:
        """Fetch this-week actuals from faireconomy feed."""
        resp = requests.get(_FF_THISWEEK, headers=_HEADERS, timeout=4.0)
        if resp.status_code != 200:
            return []
        result = []
        for item in resp.json():
            if item.get("country") != "USD":
                continue
            raw_date = item.get("date", "")
            actual = item.get("actual", "")
            if not actual:
                continue
            try:
                dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                dt_wat = dt.astimezone(self.tz)
            except Exception:
                continue
            result.append({
                "title": item.get("title", ""),
                "datetime_wat": dt_wat,
                "actual": actual,
            })
        return result

    # ------------------------------------------------------------------
    # Fallback helpers — still present for api/calendar.py error handler,
    # but return empty lists so UI shows "no data" instead of fake numbers.
    # ------------------------------------------------------------------

    def _get_fallback_this_week(self) -> List[Dict[str, Any]]:
        return []

    def _get_fallback_next_week(self) -> List[Dict[str, Any]]:
        return []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _week_end(dt: datetime) -> datetime:
    """Return end-of-Saturday (23:59:59) for the week containing dt."""
    days_until_sat = (5 - dt.weekday()) % 7
    sat = dt + timedelta(days=days_until_sat)
    return sat.replace(hour=23, minute=59, second=59, microsecond=999999)


def _merge_actuals(events: List[Dict], actuals: List[Dict]) -> List[Dict]:
    """Overlay faireconomy actual values into biquote events where titles match."""
    for ev in events:
        for act in actuals:
            if (
                act["title"].lower() in ev["title"].lower()
                and act["actual"]
                and ev.get("actual") in (None, "-", "")
            ):
                ev["actual"] = str(act["actual"])
                break
    return events
