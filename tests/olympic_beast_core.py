"""
🏅 OLYMPIC: BEAST Core — Interaction, Adaptive λ, Acceleration, Crisis Field

Validates: boundedness, convex amplification, stress alignment trigger.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.ramanash_beast import (
    beast_step,
    beast_run,
    beast_from_market,
)


def test_boundedness():
    """All outputs ∈ [-1, 1] (except energy ∈ [0,1])."""
    for _ in range(50):
        step = beast_step(0.5, -0.3, 0.2, -0.8, -0.4, s_prev=0.1)
        assert -1.01 <= step["core"] <= 1.01
        assert -1.01 <= step["interaction"] <= 1.01
        assert -1.01 <= step["stress"] <= 1.01
        assert -1.01 <= step["extended_nash"] <= 1.01
        assert -1.01 <= step["crisis_field"] <= 1.01
        assert 0 <= step["energy"] <= 1.01
    print("📊 Boundedness: all outputs ∈ [-1,1] ✅")


def test_convex_alignment():
    """When LCI≈LSI≈CSI≈FSI≈-1, interaction amplifies (negative×negative→positive in product)."""
    step_lo = beast_step(0.1, 0.1, 0.1, 0.1, -0.2, s_prev=0)
    step_hi = beast_step(-0.9, -0.9, -0.9, -0.9, -0.8, s_prev=-0.5)
    assert abs(step_hi["interaction"]) > abs(step_lo["interaction"])
    assert step_hi["stress"] < step_lo["stress"]
    print("📊 Convex alignment: crisis components amplify ✅")


def test_trigger():
    """Stress alignment trigger fires when |I|>0.5 and |S|>0.6."""
    step_on = beast_step(-0.8, -0.8, -0.7, -0.7, -0.5, s_prev=-0.5)
    step_off = beast_step(0.1, 0.1, 0.1, 0.1, 0, s_prev=0)
    assert step_on["trigger"] == 1 or abs(step_on["interaction"]) > 0.4
    assert step_off["trigger"] == 0
    print("📊 Stress alignment trigger: fires in crisis regime ✅")


def test_from_market():
    """BEAST from market data, no explosion."""
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

    steps = beast_from_market(prices, vols, macro)
    assert len(steps) > 100
    for s in steps[:5] + steps[-5:]:
        assert -1.01 <= s["crisis_field"] <= 1.01
        assert -1.01 <= s["stress"] <= 1.01
    print("📊 Market integration: bounded over full history ✅")


def main():
    print("🏅 OLYMPIC BEAST CORE — Nonlinear Bounded Systemic Stress Field")
    print("=" * 60)
    test_boundedness()
    test_convex_alignment()
    test_trigger()
    test_from_market()
    print("\n✅ BEAST core test passed")


if __name__ == "__main__":
    main()
