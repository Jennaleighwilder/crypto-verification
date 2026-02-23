"""
Test same input → same output across runs
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.verifier import verifier


def test_verify_address_consistency():
    """Same address → same output"""
    addr = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    r1 = verifier.verify_address(addr)
    r2 = verifier.verify_address(addr)
    assert r1['volatility'] == r2['volatility']
    assert r1['confidence'] == r2['confidence']
    assert r1['outperformance_vs_stoch_vol_levy'] == r2['outperformance_vs_stoch_vol_levy']


def test_33_voices_consistency():
    """Same input → same 33 Voices result"""
    addr = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    r1 = verifier.thirty_three_verify(addr)
    r2 = verifier.thirty_three_verify(addr)
    assert r1['passed'] == r2['passed']
    assert r1['confidence'] == r2['confidence']
