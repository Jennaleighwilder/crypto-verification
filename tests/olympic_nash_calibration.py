"""
🏅 OLYMPIC: Nash Confidence Calibration Test

If Nash "confidence" is calibrated: P(event|conf ∈ [a,b]) ≈ midpoint([a,b]).
If ECE > 0.10 → recommend renaming to "Nash Score" or "Nash Index".
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.ramanash_kernel import predict_macro, MACRO_FEB_23_2026
from tests.olympic_10_year_backtest import _rolling_volatility, _uvrk_predict


def main():
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'bitcoin_daily_2015_2025.json')
    if not os.path.exists(data_path):
        print("⏭️  Skipping (no data)")
        return

    with open(data_path) as f:
        data = json.load(f)
    prices = data['prices']
    vols = _rolling_volatility(prices, window=20)
    window = 60

    # Event: next 7D vol in top 20% (rolling)
    events = []
    nash_confs = []
    for i in range(window + 7, len(vols) - 7):
        hist = vols[max(0, i - 90) : i]
        if len(hist) < 30:
            continue
        thresh = sorted(hist)[max(0, int(0.8 * len(hist)) - 1)]
        next_7_vol = sum(vols[i + 1 : i + 8]) / 7 if i + 8 <= len(vols) else vols[i + 1]
        event = 1 if next_7_vol >= thresh else 0

        # Nash confidence from macro proxy (we use vol regime as proxy for macro stress)
        base_vol = vols[i]
        macro_proxy = {
            "media_sentiment": -0.5 if base_vol > 0.06 else 0.0,
            "spending_habits": 0.5,
            "war_conflict": 0.6 if base_vol > 0.05 else 0.4,
            "materials_avail": 0.5,
        }
        r = predict_macro(base_vol, macro_proxy, nash_strength=0.5, rank=0.5)
        nash_conf = r["nash_confidence"]

        events.append(event)
        nash_confs.append(nash_conf)

    if len(events) < 100:
        print("⏭️  Skipping (insufficient samples)")
        return

    # Bin into deciles
    n_bins = 10
    bins = [[] for _ in range(n_bins)]
    for e, c in zip(events, nash_confs):
        bi = min(int(c * n_bins), n_bins - 1)
        bins[bi].append(e)

    # ECE
    total = len(events)
    ece = 0.0
    print("\n📊 Nash Confidence Calibration (deciles):")
    for k in range(n_bins):
        if not bins[k]:
            continue
        n_k = len(bins[k])
        acc_k = sum(bins[k]) / n_k
        conf_k = (k + 0.5) / n_bins
        ece += (n_k / total) * abs(acc_k - conf_k)
        print(f"   Bin {k+1}: conf≈{(k+0.5)/n_bins:.2f}, actual event rate={acc_k:.3f}, n={n_k}")

    print(f"\n   ECE = {ece:.4f}")
    if ece < 0.05:
        print("   ✅ Strong calibration")
    elif ece < 0.10:
        print("   ⚠️  Acceptable calibration")
    else:
        print("   ❌ Not calibrated — recommend renaming to 'Nash Score' or 'Nash Index'")

    print("\n✅ Nash calibration test complete")


if __name__ == "__main__":
    main()
