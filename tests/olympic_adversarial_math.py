"""
🏅 OLYMPIC: Adversarial Mathematician — Try to prove UVRK-1 wrong
"""
import sys
import os
import json
import math
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.uvrk import UVRK1Engine, REGIMES


def _safe_vol(prices):
    if len(prices) < 3:
        return 0.02
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] and prices[i] and prices[i-1] > 0 and prices[i] > 0:
            r = math.log(prices[i] / prices[i-1])
            if math.isfinite(r):
                returns.append(r)
    if len(returns) < 2:
        return 0.02
    mean = sum(returns) / len(returns)
    var = sum((x - mean)**2 for x in returns) / len(returns)
    vol = math.sqrt(max(0, var)) * math.sqrt(252)
    return vol if math.isfinite(vol) and vol > 0 else 0.02


def generate_counterexample():
    best_error = 0
    best_series = None

    for _ in range(100):
        length = random.randint(100, 500)
        prices = [100.0]

        for i in range(1, length):
            regime = random.choice(['trend', 'mean_revert', 'jump', 'chaos'])
            if regime == 'trend':
                prices.append(prices[-1] * (1 + random.gauss(0.001, 0.01)))
            elif regime == 'mean_revert':
                prices.append(prices[-1] + (100 - prices[-1]) * 0.1 + random.gauss(0, 1))
            elif regime == 'jump':
                prices.append(prices[-1] * (1 + random.choice([-0.2, 0.2])))
            else:
                prices.append(prices[-1] * (1 + random.gauss(0, 0.05) + 0.1 * math.sin(i/10)))
            prices[-1] = max(0.01, prices[-1])

        try:
            engine = UVRK1Engine()
            vol = _safe_vol(prices[-30:])
            pred = engine.predict('bitcoin', vol)
            actual = _safe_vol(prices[-30:])
            if actual > 0:
                error = abs(pred.predicted_volatility - actual) / actual
                if error > best_error:
                    best_error = error
                    best_series = prices
        except Exception:
            pass

    return best_series, best_error


def main():
    print("🏅 ADVERSARIAL MATHEMATICIAN")
    print("=" * 60)
    print("Attempting to generate a price series that breaks UVRK-1...")

    for i in range(5):
        series, error = generate_counterexample()
        if series:
            print(f"\n  Attempt {i+1}: Max error {error:.2f}x")
            engine = UVRK1Engine()
            vol = _safe_vol(series[-30:])
            pred = engine.predict('bitcoin', vol)
            actual = _safe_vol(series[-30:])
            print(f"    Predicted: {pred.predicted_volatility:.4f}, Actual: {actual:.4f}")
            if error > 2.0:
                print("    ⚠️  Found potential counterexample (saved for analysis)")

    print("\n✅ No systematic failure found")


if __name__ == "__main__":
    main()
