"""
Core Macroeconomic Surprise and Directional Logic Engine for XAU/USD.
Computes component-level Z-scores, checks for internal data conflicts (whipsaw triggers),
and classifies the directional probability for Gold.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from config import EVENT_SPECS, EXECUTION_PHASES


@dataclass
class ComponentSurprise:
    key: str
    label: str
    unit: str
    actual: float
    forecast: float
    previous: Optional[float]
    surprise: float
    z_score: float
    weight: float
    gold_impact: int
    bias: str
    contribution: float


@dataclass
class EventAnalysisResult:
    event_key: str
    event_title: str
    components: List[ComponentSurprise]
    total_score: float
    overall_bias: str
    confidence_pct: float
    conflict_detected: bool
    conflict_reasons: List[str]
    expected_volatility: str
    recommended_action: str
    invalidation_rule: str
    narrative: str
    execution_guidance: Dict[str, Any] = field(default_factory=lambda: EXECUTION_PHASES)


class MacroSurpriseEngine:
    """Calculates standardized surprise scores and directional biases for XAU/USD."""

    def __init__(self):
        self.specs = EVENT_SPECS

    def analyze_event(
        self,
        event_key: str,
        user_inputs: Dict[str, Dict[str, Optional[float]]],
    ) -> EventAnalysisResult:
        """
        user_inputs format:
        {
            "headline_jobs": {"actual": 220.0, "forecast": 180.0, "previous": 175.0},
            "unemployment_rate": {"actual": 4.0, "forecast": 4.1, "previous": 4.1},
            ...
        }
        """
        if event_key not in self.specs:
            raise ValueError(f"Unknown event: {event_key}. Valid: {list(self.specs.keys())}")

        spec = self.specs[event_key]
        comp_specs = spec["components"]

        components: List[ComponentSurprise] = []
        total_score = 0.0
        bullish_weights = 0.0
        bearish_weights = 0.0
        neutral_weights = 0.0

        for comp_key, comp_info in comp_specs.items():
            input_val = user_inputs.get(comp_key, {})
            actual = input_val.get("actual")
            forecast = input_val.get("forecast")
            previous = input_val.get("previous")

            if actual is None:
                continue

            # Fallback to previous if forecast is missing
            baseline = forecast if forecast is not None else (previous if previous is not None else actual)
            surprise = actual - baseline
            std_dev = comp_info["std_dev"]
            z_score = surprise / std_dev if std_dev > 0 else 0.0

            # Component contribution to Gold:
            # gold_impact is -1 (higher actual is bearish for Gold) or +1 (higher actual is bullish for Gold)
            gold_impact = comp_info["gold_impact"]
            weight = comp_info["weight"]
            contribution = z_score * weight * gold_impact

            # Classify component bias
            # z_score significance threshold
            sig_thresh = comp_info.get("threshold_significant", std_dev * 0.7) / std_dev
            if abs(z_score) < 0.35:
                bias = "NEUTRAL"
                neutral_weights += weight
            elif contribution > 0:
                bias = "BULLISH"
                bullish_weights += weight
            else:
                bias = "BEARISH"
                bearish_weights += weight

            total_score += contribution
            components.append(
                ComponentSurprise(
                    key=comp_key,
                    label=comp_info["label"],
                    unit=comp_info["unit"],
                    actual=actual,
                    forecast=baseline,
                    previous=previous,
                    surprise=round(surprise, 4),
                    z_score=round(z_score, 2),
                    weight=weight,
                    gold_impact=gold_impact,
                    bias=bias,
                    contribution=round(contribution, 3),
                )
            )

        # Conflict Detection
        conflict_detected = False
        conflict_reasons = []

        # Check for significant conflicting component biases
        significant_bullish = [c for c in components if c.bias == "BULLISH" and abs(c.z_score) >= 0.75]
        significant_bearish = [c for c in components if c.bias == "BEARISH" and abs(c.z_score) >= 0.75]

        if significant_bullish and significant_bearish:
            conflict_detected = True
            bull_labels = ", ".join([f"{c.label} (Z: +{c.z_score})" if c.contribution > 0 else f"{c.label} (Z: {c.z_score})" for c in significant_bullish])
            bear_labels = ", ".join([f"{c.label} (Z: {c.z_score})" for c in significant_bearish])
            conflict_reasons.append(
                f"Conflicting High-Impact Indicators: Bullish component(s) [{bull_labels}] vs Bearish component(s) [{bear_labels}]."
            )

        # Specific NFP checks: Headline jobs beat vs Wage growth miss
        if event_key == "NFP":
            nfp_comp = next((c for c in components if c.key == "headline_jobs"), None)
            wage_comp = next((c for c in components if c.key == "hourly_earnings_mom"), None)
            unemp_comp = next((c for c in components if c.key == "unemployment_rate"), None)

            if nfp_comp and wage_comp:
                if nfp_comp.surprise > 30 and wage_comp.surprise <= -0.10:
                    conflict_detected = True
                    conflict_reasons.append(
                        "Divergence Alert: Headline Jobs beat strongly, but Wage Inflation slowed. The initial spike is prone to aggressive reversal."
                    )
            if nfp_comp and unemp_comp:
                if nfp_comp.surprise > 30 and unemp_comp.surprise >= 0.15:
                    conflict_detected = True
                    conflict_reasons.append(
                        "Household vs Establishment Divergence: Jobs headline beat, but Unemployment Rate unexpectedly jumped higher."
                    )

        # Overall Bias Determination
        abs_score = abs(total_score)
        if conflict_detected and abs_score < 1.3:
            overall_bias = "NEUTRAL / HIGH WHIPSAW RISK"
            confidence_pct = max(35.0, round(50.0 - abs_score * 8, 1))
            action = "AVOID INITIAL BREAKOUTS - WAIT FOR LIQUIDITY SWEEP (15-min post news)"
        elif total_score >= 1.6:
            overall_bias = "STRONG BULLISH"
            confidence_pct = min(88.0, round(65.0 + abs_score * 12, 1))
            action = "LOOK FOR PULLBACK BUYS ON 5M/15M RETEST"
        elif total_score >= 0.6:
            overall_bias = "MODERATE BULLISH"
            confidence_pct = min(72.0, round(56.0 + abs_score * 10, 1))
            action = "BULLISH BIAS - CONFIRM WITH YIELD WEAKNESS BEFORE ENTRY"
        elif total_score <= -1.6:
            overall_bias = "STRONG BEARISH"
            confidence_pct = min(88.0, round(65.0 + abs_score * 12, 1))
            action = "LOOK FOR RALLY SELLS ON 5M/15M RETEST"
        elif total_score <= -0.6:
            overall_bias = "MODERATE BEARISH"
            confidence_pct = min(72.0, round(56.0 + abs_score * 10, 1))
            action = "BEARISH BIAS - CONFIRM WITH YIELD SURGE BEFORE ENTRY"
        else:
            overall_bias = "NEUTRAL / INCONCLUSIVE"
            confidence_pct = 45.0
            action = "STAND ASIDE - DATA CLOSE TO EXPECTATIONS (RANGE TRADING)"

        # Expected Volatility
        if abs_score > 2.0 or (event_key in ["NFP", "CPI"] and abs_score > 1.2):
            expected_volatility = "EXTREME ($30 - $60+ Gold Range Expected)"
        elif abs_score > 0.8:
            expected_volatility = "HIGH ($15 - $30 Gold Range Expected)"
        else:
            expected_volatility = "MODERATE ($8 - $15 Gold Range Expected)"

        # Invalidation Rule
        if "BULLISH" in overall_bias:
            invalidation_rule = "Macro bias is invalidated if 10Y Yields (^TNX) break their pre-news daily high or if Gold breaks below the news release 5-minute candle low."
        elif "BEARISH" in overall_bias:
            invalidation_rule = "Macro bias is invalidated if 10Y Yields (^TNX) collapse below pre-news support or if Gold breaks above the news release 5-minute candle high."
        else:
            invalidation_rule = "Market is in an equilibrium/liquidity squeeze phase. Wait for range boundaries to be established."

        # Narrative generation
        narrative = self._generate_narrative(
            event_title=spec["title"],
            total_score=total_score,
            overall_bias=overall_bias,
            conflict_detected=conflict_detected,
            conflict_reasons=conflict_reasons,
            components=components,
        )

        return EventAnalysisResult(
            event_key=event_key,
            event_title=spec["title"],
            components=components,
            total_score=round(total_score, 3),
            overall_bias=overall_bias,
            confidence_pct=confidence_pct,
            conflict_detected=conflict_detected,
            conflict_reasons=conflict_reasons,
            expected_volatility=expected_volatility,
            recommended_action=action,
            invalidation_rule=invalidation_rule,
            narrative=narrative,
        )

    def _generate_narrative(
        self,
        event_title: str,
        total_score: float,
        overall_bias: str,
        conflict_detected: bool,
        conflict_reasons: List[str],
        components: List[ComponentSurprise],
    ) -> str:
        parts = [f"### Fundamental Assessment for {event_title}"]
        if conflict_detected:
            parts.append(
                "⚠️ **WHIPSAW HAZARD DETECTED**: The released report contains contradictory forces. "
                "Such prints frequently produce rapid two-sided liquidity sweeps (fakeout spikes in both directions) "
                "before the market settles."
            )
            for r in conflict_reasons:
                parts.append(f"- {r}")

        if "BULLISH" in overall_bias:
            parts.append(
                f"📈 **Directional Bias**: **{overall_bias} for XAU/USD** (Net Score: +{round(total_score, 2)}). "
                "The aggregated surprise points to weakening economic momentum or softer inflation, reducing pressure on US interest rates. "
                "This typically weakens the US Dollar and depresses US real yields, creating a supportive fundamental environment for Gold."
            )
        elif "BEARISH" in overall_bias:
            parts.append(
                f"📉 **Directional Bias**: **{overall_bias} for XAU/USD** (Net Score: {round(total_score, 2)}). "
                "The aggregated surprise points to resilient economic growth or persistent inflation, cementing expectations for higher-for-longer yields. "
                "Rising opportunity cost of holding non-yielding Gold along with Dollar strength exerts downward pressure on XAU/USD."
            )
        else:
            parts.append(
                f"⚖️ **Directional Bias**: **{overall_bias} for XAU/USD** (Net Score: {round(total_score, 2)}). "
                "The print was either closely in line with expectations or the subcomponents neutralized each other. "
                "Avoid chasing momentum; price is likely to stay contained in its technical pre-news structure."
            )

        return "\n\n".join(parts)
