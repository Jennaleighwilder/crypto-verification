"""
TORTURE TEST: Fuzzing with random byte sequences
Target: 0 crashes
"""
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.verifier import verifier
from engine.voices_33 import ThirtyThreeVoices


def generate_random_bytes(max_len=10000):
    """Generate completely random byte sequences"""
    length = random.randint(1, max_len)
    return bytes(random.getrandbits(8) for _ in range(length))


def fuzz_test(iterations=10000):
    """Fuzz the system with random byte sequences"""
    voices = ThirtyThreeVoices()

    print(f"🔪 FUZZING TEST: {iterations} random byte sequences")
    print("=" * 60)

    failures = 0

    for i in range(iterations):
        if (i + 1) % 1000 == 0:
            print(f"  {i+1}/{iterations} complete...")

        data = generate_random_bytes()

        try:
            text = data.decode('utf-8', errors='replace')
        except Exception:
            text = str(data)

        try:
            verifier.verify_address(text)
        except Exception as e:
            failures += 1
            print(f"\n⚠️ Verifier crash on iteration {i+1}: {e}")
            print(f"   Data: {data[:100]}...")

        try:
            voices.verify(text)
        except Exception as e:
            failures += 1
            print(f"\n⚠️ 33 Voices crash on iteration {i+1}: {e}")

    print("\n" + "=" * 60)
    print(f"✅ Iterations: {iterations}")
    print(f"✅ Failures: {failures}")

    assert failures == 0, f"❌ {failures} failures occurred"


if __name__ == "__main__":
    fuzz_test(10000)
    print("\n✅ torture_fuzzing PASSED")
