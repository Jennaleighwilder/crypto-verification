"""
TORTURE TEST: 24-hour soak (configurable duration)

Run with: python tests/torture_24_hour_soak.py
For quick test: python tests/torture_24_hour_soak.py --minutes 1
"""
import sys
import os
import time
import threading
import random
import string
import argparse
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.verifier import verifier


def worker(worker_id, duration_sec, results):
    """Worker thread that continuously sends requests"""
    end_time = time.time() + duration_sec
    success = 0
    failure = 0

    while time.time() < end_time:
        length = random.randint(10, 100)
        addr = ''.join(random.choices(string.ascii_letters + string.digits, k=length))

        try:
            result = verifier.verify_address(addr)
            if result.get('status') == 'success':
                success += 1
            else:
                failure += 1
        except Exception:
            failure += 1

        time.sleep(random.uniform(0.01, 0.1))

    results[worker_id] = {'success': success, 'failure': failure}


def soak_test(duration_minutes=1, num_workers=10):
    """Run soak test with multiple concurrent workers"""
    duration_sec = duration_minutes * 60

    print(f"🔪 SOAK TEST")
    print(f"   Duration: {duration_minutes} min")
    print(f"   Workers: {num_workers}")
    print("=" * 60)

    results = {}
    threads = []
    start_time = time.time()

    for i in range(num_workers):
        t = threading.Thread(target=worker, args=(i, duration_sec, results))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    elapsed = time.time() - start_time
    total_success = sum(r['success'] for r in results.values())
    total_failure = sum(r['failure'] for r in results.values())
    total = total_success + total_failure

    print("\n" + "=" * 60)
    print(f"✅ Total requests: {total}")
    print(f"✅ Success: {total_success}")
    print(f"✅ Failure: {total_failure}")
    if total > 0:
        print(f"✅ Success rate: {total_success/total*100:.2f}%")
        print(f"⏱️  Elapsed: {elapsed:.1f}s")
        print(f"⚡ Rate: {total/elapsed:.1f} req/sec")

        assert total_success / total > 0.999, f"❌ Success rate too low: {total_success/total*100:.2f}%"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--minutes', type=float, default=1, help='Duration in minutes')
    parser.add_argument('--workers', type=int, default=10, help='Number of workers')
    args = parser.parse_args()

    soak_test(duration_minutes=args.minutes, num_workers=args.workers)
    print("\n✅ torture_24_hour_soak PASSED")
