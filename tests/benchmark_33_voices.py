"""
Benchmark: 33 Voices verification time — target < 500ms
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.verifier import verifier


def test_benchmark_33_voices():
    n = 100
    start = time.perf_counter()
    for i in range(n):
        verifier.thirty_three_verify(f"bc1qtest{i}")
    elapsed = time.perf_counter() - start
    per_verify = (elapsed / n) * 1000  # ms

    print(f"Verifications: {n}")
    print(f"Total time: {elapsed:.3f}s")
    print(f"Per verification: {per_verify:.2f}ms")
    print(f"Target: < 500ms")

    assert per_verify < 500, f"Too slow: {per_verify:.2f}ms"
