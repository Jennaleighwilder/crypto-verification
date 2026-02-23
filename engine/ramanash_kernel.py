"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║              RAMANASH-ORACLE — UVRK-2 with Nash + Ramanujan                   ║
║                                                                               ║
║  "The Big Moneyball Short" — Macro-interlocked volatility oracle              ║
║  Nash equilibrium (Beautiful Mind) + Ramanujan hyper-kernel (mock-theta)      ║
║                                                                               ║
║  © 2025 Jennifer Leigh West • The Forgotten Code Research Institute           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import math
from typing import Dict, Any, Optional

from engine.uvrk import probit


def ramanujan_probit(p: float) -> float:
    """
    Ramanujan-style ultra-fast, high-precision inverse normal.
    Abramowitz-Stegun base + mock-theta inspired acceleration in tails.
    """
    if p < 0.0001:
        return -3.8
    if p > 0.9999:
        return 3.8
    base = probit(p)
    p_clip = max(0.0001, min(0.9999, p))
    t = math.sqrt(-2 * math.log(min(p_clip, 1 - p_clip)))
    accel = math.sin(math.pi * p_clip) * math.exp(-t * t / 2) * 0.07
    return base + accel if p < 0.5 else base - accel


def predict_macro(
    base_vol: float,
    macro_factors: Dict[str, float],
    nash_strength: float = 0.25,
    rank: float = 0.5,
) -> Dict[str, Any]:
    """
    Full macro interlock: media + society + demographics + war + materials.
    Nash equilibrium: volatility as game outcome between agents.
    """
    sentiment = macro_factors.get("media_sentiment", 0.5)
    spending_pressure = macro_factors.get("spending_habits", 0.5)
    geo_risk = macro_factors.get("war_conflict", 0.5)
    materials = macro_factors.get("materials_avail", 0.5)

    nash_eq = (
        sentiment * geo_risk + (1 - spending_pressure) * materials
    ) * nash_strength
    if nash_eq < 0:
        if nash_eq < -0.38:
            shock_coef = 0.75
        elif nash_eq < -0.35 and geo_risk > 0.7:
            shock_coef = 0.72
        elif nash_eq < -0.3:
            shock_coef = 0.65
        else:
            shock_coef = 0.5
        adjusted = base_vol * (1 + abs(nash_eq) * shock_coef)
    else:
        adjusted = base_vol * (1 + nash_eq)

    if abs(rank - 0.5) > 0.4:
        adjusted *= 1.25

    if geo_risk > 0.75:
        adjusted *= 1.15

    if spending_pressure < 0.45:
        adjusted *= 1.06

    if nash_eq < -0.35:
        big_short = "CRISIS BREWING"
    elif nash_eq > 0.35:
        big_short = "STEADY"
    else:
        big_short = "NEUTRAL"

    nash_confidence = 0.70 + 0.30 * abs(nash_eq)
    if geo_risk >= 0.75:
        nash_confidence = min(0.99, nash_confidence + 0.05)

    return {
        "ramanash_vol": max(0.001, adjusted),
        "nash_confidence": nash_confidence,
        "big_short_signal": big_short,
        "nash_eq": nash_eq,
        "macro_factors": macro_factors,
    }


MACRO_TARIFF_DAY_2026 = {
    "media_sentiment": -0.65,
    "spending_habits": 0.42,
    "war_conflict": 0.72,
    "materials_avail": 0.55,
}

MACRO_FEB_23_2026 = {
    "media_sentiment": -0.80,
    "spending_habits": 0.40,
    "war_conflict": 0.75,
    "materials_avail": 0.52,
}
