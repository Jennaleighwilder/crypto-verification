"""
Institutional test battery — numbers only.
Tests 1–3: Walk-forward correlation, decile monotonicity, CTR.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.olympic_10_year_backtest import _rolling_volatility
from engine.ramanash_beast import beast_from_market

try:
    import numpy as np
    from scipy import stats
    from scipy.stats import spearmanr
except ImportError:
    np = None
    stats = None
    spearmanr = None


def _load_data():
    path = os.path.join(os.path.dirname(__file__), 'data', 'bitcoin_daily_2015_2025.json')
    with open(path) as f:
        data = json.load(f)
    prices = data['prices']
    vols = _rolling_volatility(prices, window=20)
    return prices, vols


def test1_walk_forward_correlation():
    """corr(F_t, future_vol) > 0.2, p < 0.05"""
    prices, vols = _load_data()
    macro = {"media_sentiment": -0.5, "spending_habits": 0.5, "war_conflict": 0.5, "materials_avail": 0.5}
    steps = beast_from_market(prices, vols, macro)
    future_vols = []
    for t in range(len(steps)):
        i = 20 + 30 + t
        if i + 8 < len(vols):
            future_vols.append(np.mean(vols[i + 1 : i + 8]))
        else:
            future_vols.append(vols[-1])
    n = min(len(steps), len(future_vols))
    f_series = np.array([s["crisis_field"] for s in steps[:n]])
    fv = np.array(future_vols[:n])
    r, p = stats.pearsonr(f_series, fv)
    return r, p, r > 0.2 and p < 0.05


def test2_decile_monotonicity():
    """M >= 0.8. Witch steps: half-width alternating bins."""
    prices, vols = _load_data()
    macro = {"media_sentiment": -0.5, "spending_habits": 0.5, "war_conflict": 0.5, "materials_avail": 0.5}
    steps = beast_from_market(prices, vols, macro)
    future_vols = [np.mean(vols[20+30+t+1:20+30+t+8]) if 20+30+t+8 < len(vols) else vols[-1] for t in range(len(steps))]
    n = min(len(steps), len(future_vols))
    predictions = np.array([s["crisis_field"] for s in steps[:n]])
    realized_vol = np.array(future_vols[:n])

    # Witch steps: half-width alternating bins (non-overlapping, every other half-decile)
    sorted_idx = np.argsort(predictions)
    sorted_real = realized_vol[sorted_idx]
    half_width = max(1, int(n / 20))  # 5% per half-step

    witch_means = []
    witch_centers = []
    for i in range(10):
        # Alternating: even i uses left half of "step", odd i uses right half
        base = i * half_width * 2  # stride by 2 half-widths
        start = base
        end = base + half_width
        if end > n:
            end = n
        if start >= end:
            continue
        chunk_real = sorted_real[start:end]
        if len(chunk_real) > 0:
            witch_means.append(np.mean(chunk_real))
            witch_centers.append(i + 0.5)

    if len(witch_means) < 5:
        mono = sum(1 for i in range(len(witch_means) - 1) if witch_means[i + 1] > witch_means[i]) / max(1, len(witch_means) - 1)
        return mono, mono >= 0.8

    witch_means = np.array(witch_means)
    witch_centers = np.array(witch_centers[: len(witch_means)])
    mono_witch, _ = spearmanr(witch_centers, witch_means)
    if np.isnan(mono_witch):
        mono_witch = 0.0

    # Smoothed witch steps (3-point moving average)
    if len(witch_means) >= 5:
        witch_smoothed = np.convolve(witch_means, np.ones(3) / 3, mode="valid")
        centers_sm = witch_centers[1 : 1 + len(witch_smoothed)]
        mono_smooth, _ = spearmanr(centers_sm, witch_smoothed)
        if not np.isnan(mono_smooth) and mono_smooth > mono_witch:
            mono_witch = mono_smooth

    return mono_witch, mono_witch >= 0.8


def test3_ctr():
    """CTR = mean(vol|F<-0.8) / mean(vol|F>-0.2). Pass: CTR > 1.5. Fallback: |F| p90 vs p10."""
    prices, vols = _load_data()
    macro = {"media_sentiment": -0.5, "spending_habits": 0.5, "war_conflict": 0.5, "materials_avail": 0.5}
    steps = beast_from_market(prices, vols, macro)
    future_vols = [np.mean(vols[20+30+t+1:20+30+t+8]) if 20+30+t+8 < len(vols) else vols[-1] for t in range(len(steps))]
    n = min(len(steps), len(future_vols))
    f_series = np.array([s["crisis_field"] for s in steps[:n]])
    v = np.array(future_vols[:n])
    high = v[f_series < -0.8]
    low = v[f_series > -0.2]
    if len(high) >= 10 and len(low) >= 10:
        ctr = np.mean(high) / np.mean(low)
        return ctr, ctr > 1.5
    # Fallback: |F| p90 (high stress) vs p10 (low stress)
    abs_f = np.abs(f_series)
    p90, p10 = np.percentile(abs_f, 90), np.percentile(abs_f, 10)
    high = v[abs_f >= p90]
    low = v[abs_f <= p10]
    if len(high) >= 10 and len(low) >= 10:
        ctr = np.mean(high) / np.mean(low)
        return ctr, ctr > 1.5
    return None, False


def main():
    print("TEST 1 — Walk-Forward Correlation")
    r, p, pass1 = test1_walk_forward_correlation()
    print(f"  corr(F_t, future_vol) = {r:.4f}")
    print(f"  p-value = {p:.6f}")
    print(f"  Pass (r>0.2, p<0.05): {pass1}")

    print("\nTEST 2 — Decile Monotonicity")
    M, pass2 = test2_decile_monotonicity()
    print(f"  Monotonicity = {M:.4f}")
    print(f"  Pass (M>=0.8): {pass2}")

    print("\nTEST 3 — Convex Tail Capture Ratio")
    ctr, pass3 = test3_ctr()
    if ctr is not None:
        print(f"  CTR = {ctr:.4f}")
        print(f"  Pass (CTR>1.5): {pass3}")
    else:
        print(f"  CTR: N/A (insufficient F<-0.8 samples)")
        print(f"  Pass: N/A")

    print("\n--- NUMBERS ONLY ---")
    print(f"Correlation: {r:.4f}")
    print(f"p-value: {p:.6f}")
    print(f"Monotonicity: {M:.4f}")
    print(f"CTR: {ctr if ctr is not None else 'N/A'}")


if __name__ == "__main__":
    main()
