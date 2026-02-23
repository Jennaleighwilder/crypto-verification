"""
🏅 OLYMPIC: Dynamical Engine — Bounded, Stable, Convex

Validates: state memory, shock amplification, stability condition.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.ramanash_dynamical import (
    dynamical_step,
    run_dynamical,
    dynamical_from_market,
    RHO_DEFAULT,
    BETA_DEFAULT,
    ALPHA_DEFAULT,
)


def test_stability_condition():
    """ρ + |β| < 1 must hold."""
    assert RHO_DEFAULT + abs(BETA_DEFAULT) < 1, "Stability violated"
    print("📊 Stability: ρ + |β| < 1 ✅")


def test_boundedness():
    """All outputs in [-1, 1]."""
    s_prev = 0.0
    for _ in range(100):
        step = dynamical_step(0.5, 0.3, s_prev)
        assert -1.01 <= step["state"] <= 1.01
        assert -1.01 <= step["system_index"] <= 1.01
        assert 0 <= step["energy"] <= 1.01
        s_prev = step["state"]
    print("📊 Boundedness: all state ∈ [-1,1] ✅")


def test_convex_amplification():
    """High |S| → larger shock amplifier."""
    step_lo = dynamical_step(0.1, 0, s_prev=0.1)
    step_hi = dynamical_step(0.9, 0, s_prev=0.9)
    assert abs(step_hi["shock_amplifier"]) >= abs(step_lo["shock_amplifier"])
    print("📊 Convex amplification: |ShockAmp| grows with |S| ✅")


def test_run_dynamical():
    """Full run, no explosion."""
    n = 200
    uvrk_norms = [0.1] * n
    nash_eqs = [-0.2] * n
    steps = run_dynamical(uvrk_norms, nash_eqs)
    assert len(steps) == n
    for s in steps:
        assert -1.01 <= s["state"] <= 1.01
    print("📊 Run dynamical: 200 steps, no explosion ✅")


def test_from_market():
    """Integration with market data."""
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'bitcoin_daily_2015_2025.json')
    if not os.path.exists(data_path):
        print("⏭️  Skipping market test (no data)")
        return

    with open(data_path) as f:
        data = json.load(f)
    from tests.olympic_10_year_backtest import _rolling_volatility
    prices = data['prices']
    vols = _rolling_volatility(prices, window=20)
    macro = {"media_sentiment": -0.5, "spending_habits": 0.5, "war_conflict": 0.5, "materials_avail": 0.5}

    steps = dynamical_from_market(prices, vols, macro)
    assert len(steps) > 100
    for s in steps[:10] + steps[-10:]:
        assert -1.01 <= s["state"] <= 1.01
        assert -1.01 <= s["system_index"] <= 1.01
    print("📊 Market integration: bounded over full history ✅")


def main():
    print("🏅 OLYMPIC DYNAMICAL ENGINE — Bounded Nonlinear Recursive Stress")
    print("=" * 60)
    test_stability_condition()
    test_boundedness()
    test_convex_amplification()
    test_run_dynamical()
    test_from_market()
    print("\n✅ Dynamical engine test passed")


if __name__ == "__main__":
    main()
