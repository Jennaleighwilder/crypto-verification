"""
Test Φ⁻¹(p) (probit) accuracy within 0.1%
"""
import sys
import math
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.uvrk import probit

# Reference: scipy.stats.norm.ppf for accuracy check
try:
    from scipy.stats import norm
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


def test_probit_bounds():
    """Probit clips extreme values"""
    assert abs(probit(0.0001)) < 4
    assert abs(probit(0.9999)) < 4


def test_probit_symmetry():
    """Φ⁻¹(p) ≈ -Φ⁻¹(1-p)"""
    for p in [0.1, 0.2, 0.3, 0.4]:
        assert abs(probit(p) + probit(1 - p)) < 0.01


def test_probit_median():
    """Φ⁻¹(0.5) ≈ 0"""
    assert abs(probit(0.5)) < 0.001


def test_probit_accuracy_vs_scipy():
    """Probit within 0.1% of scipy norm.ppf"""
    if not HAS_SCIPY:
        import pytest
        pytest.skip("scipy not installed")
    for p in [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]:
        ours = probit(p)
        ref = norm.ppf(p)
        err = abs(ours - ref) / (abs(ref) + 1e-10)
        assert err < 0.001, f"p={p}: ours={ours}, ref={ref}, err={err}"
