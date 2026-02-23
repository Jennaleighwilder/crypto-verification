"""
Test percentile rank calculation
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.uvrk import compute_rank


def test_rank_empty_history():
    """Empty history returns 0.5"""
    r = compute_rank(0.5, [])
    assert 0.001 <= r <= 0.999


def test_rank_below_all():
    """Value below all returns low rank"""
    r = compute_rank(0.01, [0.1, 0.2, 0.3, 0.4, 0.5])
    assert r < 0.3


def test_rank_above_all():
    """Value above all returns high rank"""
    r = compute_rank(1.0, [0.1, 0.2, 0.3, 0.4, 0.5])
    assert r > 0.7


def test_rank_median():
    """Median of sorted list ~0.5"""
    hist = list(range(100))
    r = compute_rank(50, hist)
    assert 0.4 <= r <= 0.6


def test_rank_deterministic():
    """Same input → same output"""
    hist = [0.1, 0.2, 0.3, 0.4, 0.5]
    r1 = compute_rank(0.25, hist)
    r2 = compute_rank(0.25, hist)
    assert r1 == r2
