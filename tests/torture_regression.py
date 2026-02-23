"""
TORTURE TEST: Regression — known bad inputs
Target: 0 crashes (all handled gracefully)
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.verifier import verifier


def regression_test():
    """Test known problematic inputs from previous runs"""
    known_bad = [
        None,
        "",
        " ",
        "\n",
        "\t",
        "\0",
        "\\",
        "\x00\x01\x02\x03",
        "<script>alert(1)</script>",
        "'; DROP TABLE users; --",
        "../../../../etc/passwd",
        "https://evil.com/exploit",
        "😀" * 1000,
        "a" * 100000,
        "\uffff" * 100,
        "¼" * 100,
        "\u0000\uFFFF\u0001",
        "NULL",
        "undefined",
        "NaN",
        "Infinity",
        "-Infinity",
        "1e1000",
        "-1e1000",
    ]

    print("🔪 REGRESSION TEST — Known Bad Inputs")
    print("=" * 60)

    failures = 0

    for i, bad_input in enumerate(known_bad):
        try:
            result = verifier.verify_address(bad_input)
            status = "✅ Handled"
        except Exception as e:
            failures += 1
            status = f"❌ CRASH: {e}"

        disp = repr(bad_input)[:50] if bad_input is not None else "None"
        print(f"  {i+1:2d}. {disp:<50} {status}")

    print("\n" + "=" * 60)
    print(f"✅ Total tests: {len(known_bad)}")
    print(f"✅ Failures: {failures}")

    assert failures == 0, f"❌ {failures} failures occurred"


if __name__ == "__main__":
    regression_test()
    print("\n✅ torture_regression PASSED")
