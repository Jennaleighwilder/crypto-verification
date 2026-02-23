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

echo -e "\n10. Bias Stress (Purged Walk-Forward, Rolling A/B, Time-Shift)"
python tests/olympic_bias_stress.py

echo -e "\n11. Nash Calibration"
python tests/olympic_nash_calibration.py

echo -e "\n12. Macro Sensitivity (Monotonicity)"
python tests/olympic_macro_sensitivity.py

echo -e "\n13. Systemic Layer (LCI, LSI, CSI, FSI)"
python tests/olympic_systemic_layer.py

echo -e "\n14. Dynamical Engine (State Memory, Convex Amplification)"
python tests/olympic_dynamical_engine.py

echo -e "\n15. BEAST Core (Interaction, Adaptive λ, Crisis Field)"
python tests/olympic_beast_core.py

echo -e "\n16. Dominance Battery (Monotonicity, CTR, AccelEnergy)"
python tests/olympic_dominance_battery.py

echo -e "\n17. Cross-Asset Validation"
python tests/olympic_cross_asset.py

echo -e "\n🏅 OLYMPIC VALIDATION COMPLETE"
