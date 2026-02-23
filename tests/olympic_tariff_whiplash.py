"""
🏅 OLYMPIC: Tariff Whiplash — RAMANASH-ORACLE under Feb 23 2026 macro

Asserts ramanash_vol > base_vol * 1.15 and big_short_signal == "CRISIS BREWING"
when macro_factors are negative (tariff chaos).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.olympic_10_year_backtest import _rolling_volatility, _uvrk_predict
from engine.ramanash_kernel import predict_macro, MACRO_FEB_23_2026
import numpy as np


def _generate_tariff_day_prices():
    np.random.seed(20260223)
    n = 150
    prices = np.zeros(n)
    prices[0] = 58000
    for t in range(1, n):
        drift = 0.0002 + np.random.normal(0, 0.02)
        if t == n - 1:
            drift -= 0.04
        elif t >= n - 10:
            drift += np.random.normal(-0.002, 0.025)
        prices[t] = max(1000, prices[t - 1] * np.exp(drift))
    return prices.tolist()


def main():
    WINDOW = 60
    prices = _generate_tariff_day_prices()
    vols = _rolling_volatility(prices, window=20)
    idx = len(vols) - 1
    base_vol = _uvrk_predict(vols, idx, WINDOW, prices=prices[: min(20 + idx + 1, len(prices))])
    ramanash = predict_macro(base_vol, MACRO_FEB_23_2026, nash_strength=1.25, rank=0.55)

    ramanash_vol = ramanash["ramanash_vol"]
    big_short = ramanash["big_short_signal"]

    print("🏅 TARIFF WHIPLASH TEST")
    print("=" * 60)
    print(f"Base UVRK-1 vol:  {base_vol:.4f}")
    print(f"RAMANASH vol:     {ramanash_vol:.4f} (+{(ramanash_vol/base_vol - 1)*100:.1f}%)")
    print(f"Big Short Signal: {big_short}")

    assert ramanash_vol > base_vol * 1.15, (
        f"❌ RAMANASH vol ({ramanash_vol:.4f}) must exceed base by 15% (got {ramanash_vol/base_vol:.2f}x)"
    )
    assert big_short == "CRISIS BREWING", (
        f"❌ Big Short Signal must be CRISIS BREWING when macro negative (got {big_short})"
    )

    print("\n✅ Tariff whiplash test passed")


if __name__ == "__main__":
    main()
