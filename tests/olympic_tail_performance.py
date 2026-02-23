"""
🏅 OLYMPIC: Tail Performance Test — UVRK-1 on high-volatility days

Validates that regime-gated UVRK-1 improves tail win rate (target >35%).
Uses same prediction logic as 10-year backtest.
"""
import sys
import os
import math
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.olympic_10_year_backtest import (
    _rolling_volatility,
    _uvrk_predict,
    _ewma_vol,
)

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


def main():
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'bitcoin_daily_2015_2025.json')
    with open(data_path) as f:
        data = json.load(f)
    prices = data['prices']
    dates = data.get('dates', [])

    vols = _rolling_volatility(prices, window=20)
    window = 60

    # Identify tail days (top 10% by actual vol)
    n = len(vols) - window - 1
    if n < 50:
        print("❌ Insufficient data for tail test")
        return

    actual_vols = vols[window + 1 : window + n + 1]
    vol_threshold = sorted(actual_vols)[max(0, int(0.9 * n) - 1)]
    tail_idx = [j for j in range(n) if j < len(actual_vols) and actual_vols[j] >= vol_threshold]
    normal_idx = [j for j in range(n) if j not in tail_idx]

    uvrk_errors_tail = []
    ewma_errors_tail = []
    uvrk_errors_normal = []
    ewma_errors_normal = []

    for j in range(n):
        i = window + j
        v_actual = vols[i + 1]
        vol_history = vols[: i + 1]
        price_slice = prices[: 20 + i + 1]

        uvrk_pred = _uvrk_predict(vols, i, window, prices=price_slice)
        ewma_pred = _ewma_vol(vol_history)

        u_err = abs(uvrk_pred - v_actual)
        e_err = abs(ewma_pred - v_actual)

        if j in tail_idx:
            uvrk_errors_tail.append(u_err)
            ewma_errors_tail.append(e_err)
        else:
            uvrk_errors_normal.append(u_err)
            ewma_errors_normal.append(e_err)

    tail_wins = sum(1 for u, e in zip(uvrk_errors_tail, ewma_errors_tail) if u < e)
    tail_win_rate = tail_wins / len(uvrk_errors_tail) * 100 if uvrk_errors_tail else 0

    normal_wins = sum(1 for u, e in zip(uvrk_errors_normal, ewma_errors_normal) if u < e)
    normal_win_rate = normal_wins / len(uvrk_errors_normal) * 100 if uvrk_errors_normal else 0

    tail_p = 1.0
    if SCIPY_AVAILABLE and uvrk_errors_tail:
        tail_p = stats.binomtest(tail_wins, n=len(uvrk_errors_tail), p=0.5, alternative='greater').pvalue

    print("🏅 TAIL PERFORMANCE TEST")
    print("=" * 60)
    print(f"Tail days: {len(uvrk_errors_tail)} ({100 * len(uvrk_errors_tail) / n:.1f}% of sample)")
    print(f"Normal regime win rate: {normal_win_rate:.1f}%")
    print(f"Tail regime win rate:   {tail_win_rate:.1f}%")
    print(f"Tail p-value: {tail_p:.4f}")

    # Target: >35% tail win rate (up from ~20% baseline)
    assert tail_win_rate > 35, f"❌ Tail win rate too low: {tail_win_rate:.1f}% (target >35%)"

    print("\n✅ Tail performance meets target (>35%)")


if __name__ == "__main__":
    main()
