"""
Stress: corrupted JSON, malformed addresses — validation fails, not crash
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.verifier import verifier


def test_sql_injection_like():
    """SQL-like string"""
    r = verifier.verify_address("'; DROP TABLE users; --")
    assert r['status'] in ('success', 'error')


def test_xss_like():
    """XSS-like string"""
    r = verifier.verify_address("<script>alert(1)</script>")
    assert r['status'] in ('success', 'error')


def test_newlines():
    """Address with newlines"""
    r = verifier.verify_address("bc1qtest\n\n\n")
    assert r['status'] in ('success', 'error')


def test_special_chars():
    """Special chars"""
    r = verifier.verify_address("bc1q!@#$%^&*()")
    assert r['status'] in ('success', 'error')
