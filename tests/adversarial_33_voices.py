"""
Adversarial: Try to forge 33 Voices signature — must fail 100%
"""
import sys
import os
import random
import string

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.verifier import verifier


def test_forgery_random():
    """1000 random garbage inputs — none should pass"""
    attempts = 1000
    passed = 0

    for i in range(attempts):
        length = random.randint(1, 1000)
        garbage = ''.join(random.choices(
            string.ascii_letters + string.digits + string.punctuation, k=length
        ))
        result = verifier.thirty_three_verify(garbage)
        if result.get('passed'):
            passed += 1

    forgery_rate = passed / attempts
    print(f"Forgery attempts: {attempts}")
    print(f"Successful forgeries: {passed}")
    print(f"Forgery rate: {forgery_rate*100:.4f}%")
    print(f"Target: 0%")

    assert passed == 0, f"Found {passed} forged signatures!"
