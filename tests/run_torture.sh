#!/bin/bash
# Run all torture tests
# Usage: ./tests/run_torture.sh
# For 24h soak: python tests/torture_24_hour_soak.py --minutes 1440

set -e
cd "$(dirname "$0")/.."
source venv/bin/activate

echo "🔪 PHASE 6: EXTREME TORTURE TESTING"
echo "========================================"

python tests/torture_random_addresses.py
python tests/torture_mathematical_boundaries.py
python tests/torture_33_voices_exhaustive.py
python tests/torture_fuzzing.py
python tests/torture_regression.py
python tests/torture_24_hour_soak.py --minutes 0.1

echo ""
echo "✅ ALL TORTURE TESTS PASSED"
