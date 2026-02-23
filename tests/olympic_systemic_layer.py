"""
🏅 OLYMPIC: Systemic Layer — LCI, LSI, CSI, FSI + Extended Nash

Validates RAMANASH systemic extension: leverage, liquidity, credit, funding.
All indices bounded [-1,1], rolling-only, no regression.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.olympic_10_year_backtest import _rolling_volatility
from engine.ramanash_systemic import (
    systemic_stress_full,
    leverage_cycle_index,
    liquidity_spiral_index,
    credit_stress_index,
    funding_stress_index,
)
from engine.ramanash_kernel import predict_macro_systemic, MACRO_FEB_23_2026


def main():
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'bitcoin_daily_2015_2025.json')
    if not os.path.exists(data_path):
        print("⏭️  Skipping (no data)")
        return

    with open(data_path) as f:
        data = json.load(f)
    prices = data['prices']
    vols = _rolling_volatility(prices, window=20)

    print("🏅 OLYMPIC SYSTEMIC LAYER — Leverage, Liquidity, Credit, Funding")
    print("=" * 60)

    # Test indices are bounded
    for i in [100, 500, 1000, 1500]:
        if i >= len(vols) - 1:
            continue
        s = systemic_stress_full(prices, vols, i)
        for k, v in s.items():
            assert -1.01 <= v <= 1.01, f"{k}={v} out of bounds at i={i}"
        print(f"  i={i}: LCI={s['lci']:.3f} LSI={s['lsi']:.3f} CSI={s['csi']:.3f} FSI={s['fsi']:.3f} systemic={s['systemic_stress']:.3f}")

    # Extended Nash with systemic
    r = predict_macro_systemic(0.04, MACRO_FEB_23_2026, prices=prices, vols=vols, vol_idx=500)
    assert "nash_eq" in r
    assert "systemic_stress" in r
    assert "lci" in r
    assert -1.01 <= r["nash_eq"] <= 1.01
    print(f"\n  Extended Nash (macro+systemic): {r['nash_eq']:.4f}")
    print(f"  Systemic stress: {r.get('systemic_stress', 0):.4f}")
    print(f"  Big Short: {r['big_short_signal']}")

    # Macro-only fallback (no prices/vols)
    r2 = predict_macro_systemic(0.04, MACRO_FEB_23_2026)
    assert "nash_eq" in r2
    assert r2["nash_eq"] != 0  # macro produces non-zero
    print(f"\n  Macro-only fallback: nash_eq={r2['nash_eq']:.4f}")

    print("\n✅ Systemic layer test passed")


if __name__ == "__main__":
    main()
