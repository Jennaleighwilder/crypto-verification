"""
🏅 OLYMPIC: Black Swan Test — Predict extreme events
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.olympic_10_year_backtest import _rolling_volatility, _uvrk_predict


def get_black_swan_events():
    return [
        ('2020-03-12', 'COVID Crash', -50),
        ('2021-05-19', 'China Ban', -30),
        ('2022-06-18', 'Celsius', -25),
        ('2023-08-17', 'Leverage', -20),
        ('2024-03-14', 'ATH Crash', -15),
    ]


def main():
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'bitcoin_daily_2015_2025.json')
    with open(data_path) as f:
        data = json.load(f)
    prices = data['prices']
    dates = data.get('dates', [])

    vols = _rolling_volatility(prices, window=20)
    date_to_idx = {}
    for i, d in enumerate(dates):
        if d:
            date_to_idx[d[:10]] = i

    print("🏅 BLACK SWAN TEST")
    print("=" * 60)

    results = []
    for event_date, name, drop in get_black_swan_events():
        idx = date_to_idx.get(event_date)
        if idx is None:
            for d, i in date_to_idx.items():
                if event_date in d or d in event_date:
                    idx = i
                    break
        if idx is None or idx < 120:
            continue

        vol_idx = idx - 20
        if vol_idx < 60:
            continue

        predictions = {}
        for days_before in [7, 14, 30]:
            v_idx = vol_idx - days_before
            if v_idx >= 60:
                price_slice = prices[: 20 + v_idx + 1]
                predictions[f'{days_before}d_before'] = _uvrk_predict(vols, v_idx, 60, prices=price_slice)

        baseline_idxs = [j for j in range(100, vol_idx - 30, 50)]
        baseline = (
            sum(_uvrk_predict(vols, j, 60, prices=prices[: 20 + j + 1]) for j in baseline_idxs)
            / len(baseline_idxs)
            if baseline_idxs
            else 0.04
        )
        triggered = any(p > baseline * 2 for p in predictions.values())

        results.append({'event': name, 'triggered': triggered})

        print(f"\n  {name} ({event_date}):")
        for days, pred in predictions.items():
            ratio = pred / baseline if baseline > 0 else 1
            print(f"    {days}: {ratio:.2f}x baseline {'⚠️' if ratio > 2 else ''}")
        print(f"    {'✅ PREDICTED' if triggered else '❌ MISSED'}")

    if results:
        success_rate = sum(1 for r in results if r['triggered']) / len(results) * 100
        print(f"\n  Success rate: {success_rate:.1f}%")
        assert success_rate >= 20, f"❌ Only predicted {success_rate:.1f}% of black swans"

    print("\n✅ Black swan test complete")


if __name__ == "__main__":
    main()
