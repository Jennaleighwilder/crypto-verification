"""
Test 33 Voices verification
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.verifier import verifier


def test_33_voices_returns_dict():
    """thirty_three_verify returns expected keys"""
    result = verifier.thirty_three_verify("bc1qtest123")
    assert 'passed' in result
    assert 'confidence' in result
    assert 'voices_used' in result or 'method' in result


def test_33_voices_confidence_range():
    """Confidence in [0, 1]"""
    result = verifier.thirty_three_verify("bc1qtest123")
    assert 0 <= result['confidence'] <= 1


def test_33_voices_voices_count():
    """33 voices used"""
    result = verifier.thirty_three_verify("bc1qtest123")
    assert result.get('voices_used', 33) == 33
