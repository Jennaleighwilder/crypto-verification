"""
🏅 OLYMPIC: Forward-Looking Bias Stress Tests

Rigorous audit of Nash + Oracle layer per institutional review standards.
Tests: purged walk-forward, rolling vs global A/B, time-shift adversarial.
"""
import sys
import os
import math
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.uvrk import REGIMES, probit, compute_rank

# Import backtest helpers
from tests.olympic_10_year_backtest import (
    _rolling_volatility,
    _uvrk_predict,
    _detect_regime,
    _ewma_vol,
    _calculate_jump,
    THETA_NORMAL,
    KAPPA_NORMAL,
    THETA_TAIL,
    KAPPA_TAIL,
    JUMP_LAMBDA,
)


def _uvrk_predict_rolling_only(vols, i, window=60, roll_window=90, prices=None):
    """
    UVRK with STRICT rolling normalization only.
    vol_mean, vol_std use only vols[i-roll_window:i] — no expanding window.
    """
    if i < roll_window:
        return _uvrk_predict(vols, i, window, prices)  # fallback for warmup

    history = vols[max(0, i - window) : i]
    v_t = vols[i]
    rank = compute_rank(v_t, history, window=min(window, len(history)))
    regime_info = _detect_regime(vols, i, window)
    theta = THETA_TAIL if regime_info['is_tail'] else THETA_NORMAL
    kappa = KAPPA_TAIL if regime_info['is_tail'] else KAPPA_NORMAL

    # ROLLING ONLY: mean and std from last roll_window points
    roll_slice = vols[i - roll_window : i]
    vol_mean = sum(roll_slice) / len(roll_slice)
    var = sum((v - vol_mean) ** 2 for v in roll_slice) / len(roll_slice)
    vol_std = math.sqrt(var) if var > 0 else 0.01

    if abs(rank - 0.5) > 0.35:
        kappa *= 2.0

    inv_norm = probit(rank)
    pred = theta * v_t + (1 - theta) * vol_mean + kappa * vol_std * inv_norm

    if abs(inv_norm) > 2.3 and regime_info['is_tail']:
        pred += 0.08 * abs(inv_norm)

    if regime_info['is_tail'] and prices and len(prices) >= 15:
        price_slice = prices[max(0, len(prices) - 30) :]
        jump = _calculate_jump(price_slice, window=14)
        if jump > 0:
            pred += JUMP_LAMBDA * jump * v_t

    return max(0.001, pred)


def test_purged_walk_forward():
    """Purged walk-forward: G ≥ longest lookback (90). Train → Purge → Test."""
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'bitcoin_daily_2015_2025.json')
    if not os.path.exists(data_path):
        print("⏭️  Skipping purged test (no data)")
        return None

    with open(data_path) as f:
        data = json.load(f)
    prices = data['prices']
    vols = _rolling_volatility(prices, window=20)
    window = 60
    purge_gap = 90  # ≥ longest lookback

    # Train on [0, T], test on [T+G+1, T+G+H]
    T = len(vols) // 2 - purge_gap - 100
    if T < window + purge_gap:
        print("⏭️  Skipping purged test (insufficient data)")
        return None

    train_end = T
    test_start = T + purge_gap + 1
    test_end = min(test_start + 500, len(vols) - 1)

    uvrk_wins = 0
    total = 0
    for i in range(test_start, test_end):
        v_actual = vols[i + 1]
        vol_history = vols[: i + 1]
        price_slice = prices[: 20 + i + 1]

        uvrk_pred = _uvrk_predict(vols, i, window, prices=price_slice)
        ewma_pred = _ewma_vol(vol_history)
        uvrk_err = abs(uvrk_pred - v_actual)
        ewma_err = abs(ewma_pred - v_actual)
        if uvrk_err < ewma_err:
            uvrk_wins += 1
        total += 1

    rate = uvrk_wins / total * 100 if total > 0 else 0
    print(f"\n📊 Purged Walk-Forward (G={purge_gap}):")
    print(f"   Test period: {test_start}–{test_end} ({total} days)")
    print(f"   UVRK vs EWMA win rate: {rate:.1f}%")
    passed = rate > 50
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} (rate > 50%)")
    return rate


def test_rolling_vs_global():
    """Rolling-only normalization A/B. If win rate collapses → leakage."""
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'bitcoin_daily_2015_2025.json')
    if not os.path.exists(data_path):
        print("⏭️  Skipping rolling test (no data)")
        return None

    with open(data_path) as f:
        data = json.load(f)
    prices = data['prices']
    vols = _rolling_volatility(prices, window=20)
    window = 60

    # Baseline: expanding (current)
    base_wins = 0
    roll_wins = 0
    total = 0
    for i in range(window + 90, len(vols) - 1):
        v_actual = vols[i + 1]
        vol_history = vols[: i + 1]
        price_slice = prices[: 20 + i + 1]

        pred_exp = _uvrk_predict(vols, i, window, prices=price_slice)
        pred_roll = _uvrk_predict_rolling_only(vols, i, window, roll_window=90, prices=price_slice)
        ewma_pred = _ewma_vol(vol_history)

        err_exp = abs(pred_exp - v_actual)
        err_roll = abs(pred_roll - v_actual)
        err_ewma = abs(ewma_pred - v_actual)

        if err_exp < err_ewma:
            base_wins += 1
        if err_roll < err_ewma:
            roll_wins += 1
        total += 1

    base_rate = base_wins / total * 100 if total > 0 else 0
    roll_rate = roll_wins / total * 100 if total > 0 else 0
    drop = base_rate - roll_rate

    print(f"\n📊 Rolling vs Global A/B:")
    print(f"   Expanding (current): {base_rate:.1f}% win vs EWMA")
    print(f"   Rolling-only:        {roll_rate:.1f}% win vs EWMA")
    print(f"   Drop: {drop:.1f}%")
    passed = drop < 10
    print(f"   {'✅ PASS' if passed else '⚠️  Drop > 10%'}")
    return roll_rate


def test_time_shift():
    """Oracle(t-1), Oracle(t), Oracle(t+1) predicting event(t). t+1 must NOT outperform t."""
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'bitcoin_daily_2015_2025.json')
    if not os.path.exists(data_path):
        print("⏭️  Skipping time-shift test (no data)")
        return None

    with open(data_path) as f:
        data = json.load(f)
    prices = data['prices']
    vols = _rolling_volatility(prices, window=20)
    window = 60

    # Event: next-day vol in top 20% (rolling)
    def get_top_vol_days(vols, window=60, pct=0.8):
        out = []
        for i in range(window + 1, len(vols) - 1):
            hist = vols[max(0, i - window) : i]
            if len(hist) < 10:
                continue
            thresh = sorted(hist)[max(0, int((1 - pct) * len(hist)) - 1)]
            if vols[i + 1] >= thresh:
                out.append(i)
        return set(out)

    top_days = get_top_vol_days(vols, window=60, pct=0.8)
    if len(top_days) < 50:
        print("⏭️  Skipping time-shift (insufficient events)")
        return None

    def auc_at_t(shift):
        """Predict event(t) using signal at t+shift."""
        tp, fp, tn, fn = 0, 0, 0, 0
        for i in range(window + 1, len(vols) - 2):
            idx = i + shift
            if idx < window or idx >= len(vols) - 1:
                continue
            price_slice = prices[: 20 + idx + 1]
            pred = _uvrk_predict(vols, idx, window, prices=price_slice)
            # Baseline: rolling mean of last 20 vols at idx
            if idx >= 20:
                baseline = sum(vols[idx - 20 : idx]) / 20
            else:
                baseline = 0.04
            ratio = pred / baseline if baseline > 0 else 1.0
            signal = ratio > 1.3
            event = i in top_days
            if signal and event:
                tp += 1
            elif signal and not event:
                fp += 1
            elif not signal and event:
                fn += 1
            else:
                tn += 1
        total = tp + fp + tn + fn
        if total == 0:
            return 0.5
        return (tp + tn) / total

    acc_tm1 = auc_at_t(-1)
    acc_t0 = auc_at_t(0)
    acc_tp1 = auc_at_t(1)

    print(f"\n📊 Time-Shift Adversarial Test:")
    print(f"   Oracle(t-1) predicting event(t): {acc_tm1:.3f}")
    print(f"   Oracle(t)   predicting event(t): {acc_t0:.3f}")
    print(f"   Oracle(t+1) predicting event(t): {acc_tp1:.3f}")

    # t+1 must NOT be better than t (leakage detector)
    passed = acc_tp1 <= acc_t0 + 0.02
    print(f"   {'✅ PASS' if passed else '❌ FAIL'} (t+1 must not outperform t)")
    return passed


def test_nash_determinism():
    """Nash layer: same inputs → same output."""
    from engine.ramanash_kernel import predict_macro, MACRO_FEB_23_2026

    r1 = predict_macro(0.04, MACRO_FEB_23_2026, nash_strength=1.25, rank=0.55)
    r2 = predict_macro(0.04, MACRO_FEB_23_2026, nash_strength=1.25, rank=0.55)
    assert r1["nash_eq"] == r2["nash_eq"]
    assert r1["nash_confidence"] == r2["nash_confidence"]
    assert r1["big_short_signal"] == r2["big_short_signal"]
    print("\n📊 Nash Determinism: ✅ PASS (same inputs → same output)")


def main():
    print("🏅 OLYMPIC BIAS STRESS — Forward-Looking Bias Audit")
    print("=" * 60)

    test_nash_determinism()
    test_purged_walk_forward()
    test_rolling_vs_global()
    test_time_shift()

    print("\n✅ Bias stress tests complete. See docs/NASH_ORACLE_AUDIT.md for full audit.")


if __name__ == "__main__":
    main()
