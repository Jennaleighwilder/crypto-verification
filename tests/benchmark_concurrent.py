"""
Benchmark: Requests per second — target > 100/sec
"""
import sys
import os
import time
import concurrent.futures

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.verifier import verifier


def test_benchmark_concurrent():
    n = 500
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
        list(ex.map(lambda i: verifier.verify_address(f"bc1q{i}"), range(n)))
    elapsed = time.perf_counter() - start
    rps = n / elapsed

    print(f"Requests: {n}")
    print(f"Total time: {elapsed:.3f}s")
    print(f"Throughput: {rps:.0f} req/sec")
    print(f"Target: > 100/sec")

    assert rps > 100, f"Too slow: {rps:.0f} req/sec"
