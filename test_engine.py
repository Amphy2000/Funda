"""
Automated tests for XAU/USD Macro & News Directional Predictor.
"""

from macro_engine import MacroSurpriseEngine
from market_data import MarketDataManager
from historical_cases import HISTORICAL_CASES


def test_soft_cpi_bullish():
    engine = MacroSurpriseEngine()
    inputs = {
        "core_cpi_mom": {"actual": 0.15, "forecast": 0.30, "previous": 0.30},
        "headline_cpi_mom": {"actual": 0.05, "forecast": 0.20, "previous": 0.30},
        "core_cpi_yoy": {"actual": 3.3, "forecast": 3.5, "previous": 3.6},
        "headline_cpi_yoy": {"actual": 3.1, "forecast": 3.4, "previous": 3.4},
    }
    result = engine.analyze_event("CPI", inputs)
    assert "BULLISH" in result.overall_bias
    assert result.confidence_pct >= 65.0
    assert not result.conflict_detected
    assert result.total_score > 0
    print("[PASS] test_soft_cpi_bullish passed")


def test_hot_cpi_bearish():
    engine = MacroSurpriseEngine()
    inputs = {
        "core_cpi_mom": {"actual": 0.45, "forecast": 0.30, "previous": 0.30},
        "headline_cpi_mom": {"actual": 0.40, "forecast": 0.20, "previous": 0.20},
        "core_cpi_yoy": {"actual": 3.8, "forecast": 3.5, "previous": 3.5},
        "headline_cpi_yoy": {"actual": 3.7, "forecast": 3.3, "previous": 3.3},
    }
    result = engine.analyze_event("CPI", inputs)
    assert "BEARISH" in result.overall_bias
    assert result.confidence_pct >= 65.0
    assert not result.conflict_detected
    assert result.total_score < 0
    print("[PASS] test_hot_cpi_bearish passed")


def test_nfp_conflict_detection():
    engine = MacroSurpriseEngine()
    # Headline jobs beat by 80k (bearish for gold), but hourly earnings missed by -0.20% (cooling wage inflation = bullish for gold)
    inputs = {
        "headline_jobs": {"actual": 260.0, "forecast": 180.0, "previous": 170.0},
        "unemployment_rate": {"actual": 4.1, "forecast": 4.0, "previous": 4.0},
        "hourly_earnings_mom": {"actual": 0.10, "forecast": 0.30, "previous": 0.30},
        "hourly_earnings_yoy": {"actual": 3.5, "forecast": 3.8, "previous": 3.8},
    }
    result = engine.analyze_event("NFP", inputs)
    assert result.conflict_detected is True
    assert len(result.conflict_reasons) > 0
    assert "WHIPSAW" in result.overall_bias or result.confidence_pct <= 60.0
    print("[PASS] test_nfp_conflict_detection passed")


def test_historical_cases():
    engine = MacroSurpriseEngine()
    for case in HISTORICAL_CASES:
        res = engine.analyze_event(case["event_key"], case["inputs"])
        assert res is not None
        assert res.overall_bias is not None
        assert res.confidence_pct > 0
    print(f"[PASS] All {len(HISTORICAL_CASES)} historical cases evaluated successfully")


def test_market_data_fallback():
    mdm = MarketDataManager()
    corrs = mdm.calculate_correlations(period="1mo")
    assert "gold_vs_yield" in corrs
    assert "gold_vs_dxy" in corrs
    print("[PASS] test_market_data_fallback passed")


if __name__ == "__main__":
    test_soft_cpi_bullish()
    test_hot_cpi_bearish()
    test_nfp_conflict_detection()
    test_historical_cases()
    test_market_data_fallback()
    print("\nALL ENGINE TESTS PASSED!")
