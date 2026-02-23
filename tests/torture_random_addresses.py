"""
TORTURE TEST: 10,000 random addresses (including malformed)
Target: 0 crashes
"""
import sys
import os
import random
import string
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.verifier import verifier


def generate_random_address():
    """Generate random crypto-style addresses including garbage"""
    types = [
        lambda: '1' + ''.join(random.choices(string.ascii_letters + string.digits, k=33)),
        lambda: 'bc1q' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=38)),
        lambda: '0x' + ''.join(random.choices('0123456789abcdef', k=40)),
        lambda: ''.join(random.choices(string.ascii_letters + string.digits, k=44)),
        lambda: ''.join(random.choices(string.printable, k=random.randint(1, 1000))),
        lambda: '',
        lambda: None,
        lambda: '😀' * 100,
        lambda: '<script>alert("xss")</script>',
        lambda: '../../../../etc/passwd',
    ]
    return random.choice(types)()


def torture_test():
    """Run 10,000 random addresses through the verifier — no crashes"""
    total = 10000
    success = 0
    errors = 0
    crashes = 0
    crash_details = []
    start_time = time.time()

    print(f"🔪 TORTURE TEST: {total} random addresses")
    print("=" * 60)

    for i in range(total):
        addr = generate_random_address()
        try:
            result = verifier.verify_address(addr)
            if result.get('status') == 'success':
                success += 1
            else:
                errors += 1
        except Exception as e:
            crashes += 1
            crash_details.append((repr(addr)[:80], str(e)))

        if (i + 1) % 1000 == 0:
            print(f"  {i+1}/{total} complete...")

    elapsed = time.time() - start_time

    print("\n" + "=" * 60)
    print(f"✅ Success (status=success): {success}")
    print(f"⚠️  Handled (status=error): {errors}")
    print(f"❌ Crashes: {crashes}")
    print(f"⏱️  Time: {elapsed:.2f}s")
    print(f"⚡ Rate: {total/elapsed:.1f} addresses/sec")

    if crash_details:
        print("\n⚠️ Crashes:")
        for addr, err in crash_details[:10]:
            print(f"  {addr} → {err}")

    assert crashes == 0, f"❌ {crashes} crashes occurred"


if __name__ == "__main__":
    torture_test()
    print("\n✅ torture_random_addresses PASSED")
