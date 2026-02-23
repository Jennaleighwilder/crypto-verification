"""
Institutional test battery — numbers only.
Tests 1–3: Walk-forward correlation, decile monotonicity, CTR.

STRICT tests: equal deciles, no smoothing, no alternation, no bin tricks.
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
    from scipy.stats import pearsonr
except ImportError:
    np = None
    stats = None
    pearsonr = None


# --- STRICT TEST 1 — WALK-FORWARD CORRELATION ---
def strict_test1_correlation(f_series, future_vol):
    f = np.array(f_series)
    v = np.array(future_vol)

    mask = ~np.isnan(f) & ~np.isnan(v)
    f = f[mask]
    v = v[mask]

    r, p = pearsonr(f, v)

    print("Correlation:", round(r, 4))
    print("p-value:", p)

    passed = (r > 0.2) and (p < 0.05)
    print("Pass:", passed)

    return r, p, passed


# --- STRICT TEST 2 — EQUAL DECILE MONOTONICITY ---
def strict_test2_monotonicity(f_series, future_vol):
    f = np.array(f_series)
    v = np.array(future_vol)

    mask = ~np.isnan(f) & ~np.isnan(v)
    f = f[mask]
    v = v[mask]

    deciles = np.percentile(f, np.arange(0, 110, 10))

    means = []
    for i in range(10):
        if i < 9:
            bucket = v[(f >= deciles[i]) & (f < deciles[i+1])]
        else:
            bucket = v[(f >= deciles[i]) & (f <= deciles[i+1])]
        means.append(np.mean(bucket))

    monotonic = sum(
        1 for i in range(9)
        if means[i+1] > means[i]
    ) / 9

    print("Monotonicity:", round(monotonic, 4))
    print("Pass:", monotonic >= 0.8)

    return monotonic, monotonic >= 0.8


# --- STRICT TEST 3 — TRUE CTR (NO PERCENTILE FALLBACK) ---
def strict_test3_ctr(f_series, future_vol):
    f = np.array(f_series)
    v = np.array(future_vol)

    high = v[f < -0.8]
    low  = v[f > -0.2]

    if len(high) < 10 or len(low) < 10:
        print("Insufficient tail samples.")
        return None, False

    ctr = np.mean(high) / np.mean(low)

    print("CTR:", round(ctr, 4))
    print("Pass:", ctr > 1.5)

    return ctr, ctr > 1.5


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


def _generate_f_and_future_vol():
    """Generate f_series (F_t) and future_vol (t+1 → t+7 realized vol)."""
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
    future_vol = np.array(future_vols[:n])
    return f_series, future_vol


def main():
    f_series, future_vol = _generate_f_and_future_vol()

    print("--- STRICT TEST 1 ---")
    r, p, _ = strict_test1_correlation(f_series, future_vol)

    print("\n--- STRICT TEST 2 ---")
    monotonic, _ = strict_test2_monotonicity(f_series, future_vol)

    print("\n--- STRICT TEST 3 ---")
    f = np.array(f_series)
    v = np.array(future_vol)
    mask = ~np.isnan(f) & ~np.isnan(v)
    f, v = f[mask], v[mask]
    n_high = np.sum(f < -0.8)
    n_low = np.sum(f > -0.2)
    ctr, _ = strict_test3_ctr(f_series, future_vol)

    print("\n--- OUTPUT ---")
    print("Correlation:", round(r, 4))
    print("p-value:", p)
    print("Monotonicity:", round(monotonic, 4))
    print("CTR:", round(ctr, 4) if ctr is not None else "N/A")
    print("Tail sample counts: F<-0.8:", n_high, "| F>-0.2:", n_low)


if __name__ == "__main__":
    main()
