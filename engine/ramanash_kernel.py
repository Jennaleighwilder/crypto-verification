"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║              RAMANASH-ORACLE — UVRK-2 with Ramanujan hyper-kernel             ║
║                                                                               ║
║  "The Big Moneyball Short" — Macro-interlocked volatility oracle              ║
║  RAMANASH composite index (macro stress) + Ramanujan probit (mock-theta)      ║
║                                                                               ║
║  © 2025 Jennifer Leigh West • The Forgotten Code Research Institute           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

# Threshold provenance: frozen 2025-02-23, not tuned on data. See docs/MACRO_WEIGHTING_AUDIT.md
THRESHOLD_CRISIS = -0.35
THRESHOLD_STEADY = 0.35
THRESHOLD_SHOCK_HIGH = -0.38
THRESHOLD_SHOCK_MID = -0.35
THRESHOLD_SHOCK_LOW = -0.30

import math
from typing import Dict, Any, Optional, List

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
    RAMANASH composite index: media + spending + war + materials.
    Macro stress index (not game-theoretic equilibrium) — volatility adjustment.
    """
    sentiment = macro_factors.get("media_sentiment", 0.5)
    spending_pressure = macro_factors.get("spending_habits", 0.5)
    geo_risk = macro_factors.get("war_conflict", 0.5)
    materials = macro_factors.get("materials_avail", 0.5)

    nash_eq = (
        sentiment * geo_risk + (1 - spending_pressure) * materials
    ) * nash_strength
    if nash_eq < 0:
        if nash_eq < THRESHOLD_SHOCK_HIGH:
            shock_coef = 0.75
        elif nash_eq < THRESHOLD_SHOCK_MID and geo_risk > 0.7:
            shock_coef = 0.72
        elif nash_eq < THRESHOLD_SHOCK_LOW:
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

    if nash_eq < THRESHOLD_CRISIS:
        big_short = "CRISIS BREWING"
    elif nash_eq > THRESHOLD_STEADY:
        big_short = "STEADY"
    else:
        big_short = "NEUTRAL"

    # Nash score: 0.70 + 0.30*|nash_eq|. Not calibrated; use "score" for institutional clarity.
    nash_score = 0.70 + 0.30 * abs(nash_eq)
    if geo_risk >= 0.75:
        nash_score = min(0.99, nash_score + 0.05)

    return {
        "ramanash_vol": max(0.001, adjusted),
        "nash_confidence": nash_score,  # backward compat; prefer nash_score
        "nash_score": nash_score,
        "big_short_signal": big_short,
        "nash_eq": nash_eq,
        "macro_factors": macro_factors,
    }


def predict_macro_systemic(
    base_vol: float,
    macro_factors: Dict[str, float],
    prices: Optional[List[float]] = None,
    vols: Optional[List[float]] = None,
    vol_idx: Optional[int] = None,
    nash_strength: float = 0.25,
    rank: float = 0.5,
    lambda_macro: float = 0.5,
    vol_offset: int = 20,
) -> Dict[str, Any]:
    """
    Extended RAMANASH: MacroStress + SystemicStress.
    ExtendedNashEq = λ * MacroStress + (1-λ) * SystemicStress.
    When prices/vols/vol_idx provided, uses full systemic layer. Else macro-only.
    """
    macro_result = predict_macro(base_vol, macro_factors, nash_strength, rank)
    macro_stress = macro_result["nash_eq"]

    if prices and vols is not None and vol_idx is not None and len(prices) >= vol_offset + vol_idx and len(vols) > vol_idx:
        try:
            from engine.ramanash_systemic import systemic_stress_full
            systemic = systemic_stress_full(prices, vols, vol_idx, vol_offset)
            systemic_val = systemic["systemic_stress"]
            extended_nash = lambda_macro * macro_stress + (1 - lambda_macro) * systemic_val
            extended_nash = max(-1.0, min(1.0, extended_nash))
        except Exception:
            extended_nash = macro_stress
            systemic = {}
    else:
        extended_nash = macro_stress
        systemic = {}

    # Apply same shock/vol logic using extended_nash
    sentiment = macro_factors.get("media_sentiment", 0.5)
    spending_pressure = macro_factors.get("spending_habits", 0.5)
    geo_risk = macro_factors.get("war_conflict", 0.5)

    if extended_nash < 0:
        if extended_nash < THRESHOLD_SHOCK_HIGH:
            shock_coef = 0.75
        elif extended_nash < THRESHOLD_SHOCK_MID and geo_risk > 0.7:
            shock_coef = 0.72
        elif extended_nash < THRESHOLD_SHOCK_LOW:
            shock_coef = 0.65
        else:
            shock_coef = 0.5
        adjusted = base_vol * (1 + abs(extended_nash) * shock_coef)
    else:
        adjusted = base_vol * (1 + extended_nash)

    if abs(rank - 0.5) > 0.4:
        adjusted *= 1.25
    if geo_risk > 0.75:
        adjusted *= 1.15
    if spending_pressure < 0.45:
        adjusted *= 1.06

    if extended_nash < THRESHOLD_CRISIS:
        big_short = "CRISIS BREWING"
    elif extended_nash > THRESHOLD_STEADY:
        big_short = "STEADY"
    else:
        big_short = "NEUTRAL"

    nash_score = 0.70 + 0.30 * abs(extended_nash)
    if geo_risk >= 0.75:
        nash_score = min(0.99, nash_score + 0.05)

    out = {
        "ramanash_vol": max(0.001, adjusted),
        "nash_confidence": nash_score,
        "nash_score": nash_score,
        "big_short_signal": big_short,
        "nash_eq": extended_nash,
        "macro_factors": macro_factors,
        "macro_stress": macro_stress,
    }
    if systemic:
        out["systemic_stress"] = systemic.get("systemic_stress", 0)
        out["lci"] = systemic.get("lci")
        out["lsi"] = systemic.get("lsi")
        out["csi"] = systemic.get("csi")
        out["fsi"] = systemic.get("fsi")
    return out


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
