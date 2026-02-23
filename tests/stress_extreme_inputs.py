"""
Stress: garbage inputs — graceful error, no crash
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.verifier import verifier


def test_empty_string():
    """Empty address"""
    r = verifier.verify_address("")
    assert r['status'] in ('success', 'error')
    assert 'address' in r or 'error' in r


def test_very_long_string():
    """1M chars"""
    addr = "x" * 1_000_000
    r = verifier.verify_address(addr)
    assert r['status'] in ('success', 'error')


def test_unicode_emoji():
    """Emoji in address"""
    r = verifier.verify_address("bc1q🔥🔥🔥🔥")
    assert r['status'] in ('success', 'error')


def test_binary_like():
    """Binary-like bytes"""
    r = verifier.verify_address("\x00\x01\x02\xff")
    assert r['status'] in ('success', 'error')


def test_none():
    """None raises or returns error"""
    try:
        r = verifier.verify_address(None)
        assert r.get('status') == 'error' or 'error' in r
    except (TypeError, AttributeError):
        pass  # Expected


def test_verify_address_handles_empty():
    """verify_address with empty string doesn't crash"""
    r = verifier.verify_address("")
    assert 'status' in r
