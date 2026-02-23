"""
🏅 OLYMPIC: Oracle Test — Predict the unpredictable (crisis periods)
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.olympic_10_year_backtest import _rolling_volatility, _uvrk_predict


def get_crisis_periods():
    return [
        ('2020-03-12', 'COVID Crash', 50),
        ('2021-05-19', 'China Ban Crash', 30),
        ('2022-06-18', 'Celsius Collapse', 25),
        ('2023-08-17', 'Leverage Washout', 20),
        ('2024-03-14', 'ATH then crash', 15),
    ]


def main():
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'bitcoin_daily_2015_2025.json')
    with open(data_path) as f:
        data = json.load(f)
    prices = data['prices']
    dates = data.get('dates', [])

    vols = _rolling_volatility(prices, window=20)
    date_to_idx = {d: i for i, d in enumerate(dates)} if dates else {}

    print("🏅 ORACLE TEST — Predicting the Unpredictable")
    print("=" * 60)

    predicted = 0
    total = 0

    for crisis_date, name, drop_pct in get_crisis_periods():
        idx = date_to_idx.get(crisis_date)
        if idx is None:
            for i, d in enumerate(dates):
                if d and crisis_date in d:
                    idx = i
                    break
        if idx is None or idx < 60:
            continue

        vol_idx = idx - 20 - 1
        price_slice = prices[: 20 + vol_idx + 1]
        pred_vol = _uvrk_predict(vols, vol_idx, 60, prices=price_slice)
        baseline_idxs = [100, 200, 300, 400, 500]
        baseline_idxs = [j for j in baseline_idxs if j < idx - 30]
        if not baseline_idxs:
            continue
        baseline = sum(
            _uvrk_predict(vols, j - 20 - 1, 60, prices=prices[: 20 + j]) for j in baseline_idxs
        ) / len(baseline_idxs)
        ratio = pred_vol / baseline if baseline > 0 else 1.0

        print(f"\n  {name} ({crisis_date}):")
        print(f"    Actual drop: {drop_pct}%")
        print(f"    Predicted volatility ratio: {ratio:.2f}x baseline")
        status = "✅ PREDICTED" if ratio > 1.5 else "❌ MISSED"
        print(f"    {status}")

        total += 1
        if ratio > 1.5:
            predicted += 1

    if total > 0:
        rate = predicted / total * 100
        print(f"\n  Success rate: {rate:.1f}% ({predicted}/{total})")
        assert rate >= 40, f"❌ Only predicted {rate:.1f}% of crises"

    print("\n✅ Oracle test complete")


if __name__ == "__main__":
    main()
