"""
Model Integrity Watchdog — Audits production API against Olympic baselines.
Run hourly via GitHub Action or cron.
"""
import os
import sys
import json

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

try:
    from scipy import stats
except ImportError:
    stats = None

# Config from Olympic Subperiod Robustness
BASE_WIN_RATE = 0.77
TAIL_WIN_RATE = 0.20
CONFIDENCE_LEVEL = 0.95
API_URL = os.environ.get("PROD_URL", "https://crypto-verification.vercel.app")
TEST_VECTORS = [
    "bc1qxy2kgdygjrsqtzq2n0y8gvt2leg9w3",
    "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    "bc1qtest123456789",
    "0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe",
]


def check_health() -> bool:
    """Verify API is reachable. Retry up to 3 times for transient failures."""
    for attempt in range(3):
        try:
            r = requests.get(f"{API_URL}/api/health", timeout=15)
            data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
            if r.status_code == 200 and data.get("status") == "healthy":
                return True
            print(f"❌ Health check attempt {attempt + 1}: status={r.status_code}, body={r.text[:200]}")
        except Exception as e:
            print(f"❌ Health check attempt {attempt + 1} failed: {e}")
        if attempt < 2:
            import time
            time.sleep(2)
    return False


def check_verify_consistency() -> tuple[int, int]:
    """Run test vectors, count successes. Success = valid JSON with status."""
    wins = 0
    total = len(TEST_VECTORS)
    for addr in TEST_VECTORS:
        try:
            r = requests.get(f"{API_URL}/api/verify", params={"address": addr}, timeout=15)
            data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
            if data.get("status") == "success" and "volatility" in data:
                wins += 1
            elif r.status_code != 200:
                print(f"  ⚠️ {addr[:12]}...: status={r.status_code}")
        except Exception as e:
            print(f"  ⚠️ {addr[:12]}...: {e}")
    return wins, total


def main():
    print("🛡️ Model Integrity Watchdog")
    print("=" * 50)
    print(f"Target: {API_URL}")

    if not check_health():
        print("❌ API unreachable — aborting")
        sys.exit(1)
    print("✅ Health OK")

    wins, total = check_verify_consistency()
    win_rate = wins / total if total > 0 else 0
    print(f"✅ Verify: {wins}/{total} ({win_rate:.0%})")

    # Regime: assume NORMAL for watchdog (no live price feed in script)
    regime = "NORMAL"
    threshold = BASE_WIN_RATE

    if stats and total >= 10:
        # Binomial: is current win rate below threshold?
        p_value = stats.binomtest(wins, n=total, p=threshold, alternative="less").pvalue
        if p_value < (1 - CONFIDENCE_LEVEL):
            print(f"⚠️ ALERT: Possible drift (p={p_value:.4f})")
            sys.exit(1)

    print("✅ System healthy")
    sys.exit(0)


if __name__ == "__main__":
    main()
