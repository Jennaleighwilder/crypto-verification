#!/bin/bash
# Run Olympic validation suite
set -e
cd "$(dirname "$0")/.."
source venv/bin/activate

echo "🏅 OLYMPIC VALIDATION SUITE"
echo "=========================="

echo -e "\n1. 10-Year Backtest"
python tests/olympic_10_year_backtest.py

echo -e "\n2. Oracle Test"
python tests/olympic_oracle_test.py

echo -e "\n3. Adversarial Mathematician"
python tests/olympic_adversarial_math.py

echo -e "\n4. Calibration Test"
python tests/olympic_confidence.py

echo -e "\n5. Black Swan Test"
python tests/olympic_black_swan.py

echo -e "\n6. 33 Voices Collision (Extended)"
python tests/olympic_33_voices_collision.py

echo -e "\n7. Performance Under Load"
python tests/olympic_performance_load.py

echo -e "\n8. Tail Performance Test"
python tests/olympic_tail_performance.py

echo -e "\n9. Tariff Whiplash (RAMANASH)"
python tests/olympic_tariff_whiplash.py

echo -e "\n🏅 OLYMPIC VALIDATION COMPLETE"
