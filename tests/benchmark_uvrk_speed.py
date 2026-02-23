"""
Benchmark: UVRK prediction time — target < 100ms
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.uvrk import UVRK1Engine


def test_benchmark_uvrk_speed():
    engine = UVRK1Engine()
    n = 1000
    start = time.perf_counter()
    for i in range(n):
        engine.predict('bitcoin', 0.04 + (i % 50) / 1000)
    elapsed = time.perf_counter() - start
    per_pred = (elapsed / n) * 1000  # ms

    print(f"Predictions: {n}")
    print(f"Total time: {elapsed:.3f}s")
    print(f"Per prediction: {per_pred:.2f}ms")
    print(f"Target: < 100ms")

    assert per_pred < 100, f"Too slow: {per_pred:.2f}ms"
