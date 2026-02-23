"""
TORTURE TEST: 33 Voices exhaustive pattern search
Target: 0 collisions (each input produces unique 33-voice fingerprint)
"""
import sys
import os
import string

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.voices_33 import ThirtyThreeVoices


def test_exhaustive_patterns():
    """Test 2-char combinations for collisions — O(n²) fingerprint check"""
    voices = ThirtyThreeVoices()
    chars = string.ascii_letters + string.digits  # 62 chars
    seen = {}
    collisions = []

    total = len(chars) ** 2
    print("🔪 33 VOICES EXHAUSTIVE PATTERN TEST")
    print("=" * 60)
    print(f"Testing all {len(chars)}² = {total} 2-character combinations...")

    for i, a in enumerate(chars):
        for b in chars:
            test_str = a + b
            fp = voices.get_signature_fingerprint(test_str)
            if fp in seen:
                collisions.append((test_str, seen[fp]))
            else:
                seen[fp] = test_str

        if (i + 1) % 10 == 0:
            print(f"  {(i+1)*len(chars)}/{total} complete...")

    print("\n" + "=" * 60)
    print(f"✅ Total combinations tested: {total}")
    print(f"✅ Collisions found: {len(collisions)}")
    if collisions:
        print(f"⚠️ First 5 collisions: {collisions[:5]}")
    assert len(collisions) == 0, f"❌ Found {len(collisions)} collisions"


if __name__ == "__main__":
    test_exhaustive_patterns()
    print("\n✅ torture_33_voices_exhaustive PASSED")
