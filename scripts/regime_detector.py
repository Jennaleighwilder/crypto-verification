"""
Regime Detector — Determines Normal vs Tail (high-volatility) market state.
Used by drift monitor to adjust win-rate expectations.
"""
import math


def get_current_regime(recent_prices: list) -> str:
    """
    Determines if we are in 'Normal' or 'Tail' (Top 10%) regime.
    Uses daily log returns, annualized with √252.
    """
    if len(recent_prices) < 21:
        return "NORMAL"
    returns = []
    for i in range(1, len(recent_prices)):
        if recent_prices[i - 1] > 0 and recent_prices[i] > 0:
            returns.append(math.log(recent_prices[i] / recent_prices[i - 1]))
    if len(returns) < 10:
        return "NORMAL"
    mean = sum(returns) / len(returns)
    var = sum((r - mean) ** 2 for r in returns) / len(returns)
    current_vol = math.sqrt(max(0, var)) * math.sqrt(252)
    # Top 10% threshold for BTC (typical ~0.85+ annualized)
    if current_vol > 0.85:
        return "TAIL_EVENT"
    return "NORMAL"


def get_dynamic_threshold(regime: str) -> float:
    """Win rate threshold based on regime."""
    if regime == "TAIL_EVENT":
        return 0.20  # Documented tail sensitivity (pre-regime-gating baseline)
    return 0.77  # Subperiod robustness baseline
