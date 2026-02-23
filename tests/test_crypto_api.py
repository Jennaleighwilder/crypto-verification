"""
Test crypto API (CoinGecko/Binance when available)
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.crypto_api import get_transactions, get_stoch_vol_levy


def test_get_transactions_returns_dict():
    """get_transactions returns dict with expected keys"""
    r = get_transactions("bc1qtest123")
    assert isinstance(r, dict)
    assert 'tx_count' in r
    assert 'avg_value' in r
    assert 'age_days' in r


def test_get_transactions_deterministic():
    """Same address → same output"""
    r1 = get_transactions("bc1qtest123")
    r2 = get_transactions("bc1qtest123")
    assert r1 == r2


def test_get_stoch_vol_levy_range():
    """Benchmark in reasonable range"""
    r = get_stoch_vol_levy("bc1qtest123")
    assert 0.05 <= r <= 0.25
