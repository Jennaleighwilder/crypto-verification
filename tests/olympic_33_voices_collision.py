"""
🏅 OLYMPIC: 33 Voices Collision Test (Extended) — 17,576 3-char combinations

Tests that no two inputs in this finite sample produce the same fingerprint.
Collision resistance at scale comes from SHA256 (2^256), not from the 33 voices.
This test validates deterministic behavior on a structured sample — not global uniqueness.
"""
import sys
import os
import itertools

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.voices_33 import ThirtyThreeVoices


def main():
    voices = ThirtyThreeVoices()
    chars = 'abcdefghijklmnopqrstuvwxyz'
    total = len(chars) ** 3

    print("🏅 33 VOICES COLLISION TEST (Extended)")
    print("=" * 60)
    print(f"Testing {total:,} 3-character combinations...")

    signatures = {}
    collisions = []

    for i, combo in enumerate(itertools.product(chars, repeat=3)):
        test_str = ''.join(combo)
        sig = voices.get_signature_fingerprint(test_str)

        if sig in signatures:
            collisions.append((signatures[sig], test_str))
        else:
            signatures[sig] = test_str

        if (i + 1) % 5000 == 0:
            print(f"  {i+1}/{total} complete...")

    print("\n" + "=" * 60)
    print(f"✅ Total combinations: {total}")
    print(f"✅ Collisions found: {len(collisions)}")
    print(f"✅ Collision rate: {len(collisions)/total*100:.6f}%")

    if collisions:
        print("\n⚠️ First 10 collisions:")
        for s1, s2 in collisions[:10]:
            print(f"  '{s1}' == '{s2}'")

    assert len(collisions) == 0, f"❌ Found {len(collisions)} collisions"
    print("\n✅ 33 Voices collision test passed")


if __name__ == "__main__":
    main()
