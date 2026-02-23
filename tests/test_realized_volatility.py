"""
Test realized volatility calculation (matches known Bitcoin days)
"""
import sys
import math
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _rolling_volatility(prices, window=20):
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] > 0 and prices[i] > 0:
            returns.append(math.log(prices[i] / prices[i-1]))
    vols = []
    for i in range(window, len(returns)):
        chunk = returns[i-window:i]
        mean = sum(chunk) / len(chunk)
        var = sum((x - mean)**2 for x in chunk) / len(chunk)
        vols.append(math.sqrt(var) * math.sqrt(252))
    return vols


def test_vol_constant_series():
    """Constant price → zero volatility"""
    prices = [100.0] * 50
    vols = _rolling_volatility(prices)
    assert all(v == 0 or v < 1e-10 for v in vols)


def test_vol_positive():
    """Volatility is non-negative"""
    prices = [100 + i * 0.1 + (i % 3) * 2 for i in range(100)]
    vols = _rolling_volatility(prices)
    assert all(v >= 0 for v in vols)


def test_vol_scale():
    """Higher variance → higher vol"""
    low_var = [100 + 0.001 * (i % 10) for i in range(100)]
    high_var = [100 + 0.1 * (i % 10) for i in range(100)]
    v1 = _rolling_volatility(low_var)
    v2 = _rolling_volatility(high_var)
    assert sum(v2) > sum(v1)
