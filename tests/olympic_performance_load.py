"""
🏅 OLYMPIC: Performance Under Load Test
"""
import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.verifier import verifier


def _single_request():
    start = time.time()
    result = verifier.verify_address('bc1qtest123456789')
    elapsed = (time.time() - start) * 1000
    return elapsed, result


def _concurrent_requests(n):
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(_single_request) for _ in range(n)]
        times = []
        errors = []
        for future in as_completed(futures):
            try:
                elapsed, result = future.result()
                times.append(elapsed)
                if result.get('status') != 'success':
                    errors.append(result)
            except Exception as e:
                errors.append(str(e))
        return times, errors


def test_single_request():
    elapsed, result = _single_request()
    assert result.get('status') == 'success'
    assert elapsed < 2000


def test_concurrent_requests():
    times, errors = _concurrent_requests(100)
    assert len(errors) / 100 < 0.05
    p95_idx = min(int(len(times) * 0.95) - 1, len(times) - 1)
    assert sorted(times)[max(0, p95_idx)] < 2000


def main():
    print("🏅 PERFORMANCE UNDER LOAD TEST")
    print("=" * 60)

    times_single = []
    for _ in range(100):
        t, _ = _single_request()
        times_single.append(t)

    avg_single = sum(times_single) / len(times_single)
    p95_single = sorted(times_single)[int(len(times_single) * 0.95)]

    print(f"\n📊 Single Request (100 runs):")
    print(f"  Average: {avg_single:.2f}ms")
    print(f"  P95:     {p95_single:.2f}ms")

    for concurrency in [10, 50, 100, 500]:
        times, errors = _concurrent_requests(concurrency)

        if times:
            avg = sum(times) / len(times)
            p95 = sorted(times)[int(len(times) * 0.95)]
            print(f"\n📊 Concurrent ({concurrency}):")
            print(f"  Average: {avg:.2f}ms")
            print(f"  P95:     {p95:.2f}ms")
            print(f"  Errors:  {len(errors)}")

            assert len(errors) / concurrency < 0.05, f"❌ Error rate too high: {len(errors)/concurrency*100:.1f}%"
            assert p95 < 2000, f"❌ P95 latency too high: {p95:.2f}ms"

    print("\n✅ Performance meets Olympic standards")


if __name__ == "__main__":
    main()
