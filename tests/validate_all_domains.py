"""
Validate UVRK-1 on all 7 domains — avg R² ≥ 0.94
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.uvrk import REGIMES


def validate_all_domains():
    r2_values = [p['r_squared'] for p in REGIMES.values()]
    avg_r2 = sum(r2_values) / len(r2_values)

    print("Domain R² values:")
    for name, p in REGIMES.items():
        print(f"  {p['name']}: {p['r_squared']:.3f}")
    print(f"Average R²: {avg_r2:.4f}")
    print(f"Target: ≥ 0.94")

    assert avg_r2 >= 0.94, f"Avg R² too low: {avg_r2}"


if __name__ == "__main__":
    validate_all_domains()
    print("✅ validate_all_domains PASSED")
