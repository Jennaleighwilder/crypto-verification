# Technical Audit Response

## Summary

We addressed all valid findings from the technical audit. Some claims referred to code that does not exist in this codebase (possibly a different version or hypothetical).

---

## Fixes Implemented

### 1. Hardcoded 8.71σ Fallback — FIXED

**Issue:** When benchmark was unavailable, verifier returned hardcoded `+8.71σ`.

**Fix:** Fallback now returns `"N/A (no benchmark)"` instead of an artificial sigma. Outperformance is only reported when we have an empirical benchmark.

### 2. 33 Voices Collision Claim — CLARIFIED

**Issue:** Claim "mathematically unique" overstated. Uniqueness comes from SHA256, not the 33 voices.

**Fix:** Updated docstrings in `voices_33.py` and `olympic_33_voices_collision.py` to state:
- Collision resistance comes from SHA256 (2^256 space)
- The 33 voices provide deterministic input diversity before hashing
- The 17,576 test validates deterministic behavior on a sample — not global uniqueness

### 3. Input Validation — ADDED

**Issue:** No input validation on address.

**Fix:** Added `_validate_address()`:
- Length: 10–128 chars
- Charset: alphanumeric, 0x, bc1, common crypto chars
- Returns clear error messages for invalid input

### 4. Volatility Units — DOCUMENTED

**Issue:** Audit claimed hourly vs daily mismatch.

**Reality:** Current codebase uses daily log returns throughout. `_rolling_volatility`, `_stoch_vol_levy`, and `_uvrk_predict` all use √252 (daily annualization). No `realized_volatility` with √(252×24) exists in this repo.

**Fix:** Added explicit unit documentation to backtest module.

---

## Audit Claims Not Present in Codebase

### np / numpy in verifier.py

**Audit:** "prices.append(prices[-1] * (1 + drift + np.random.normal(0, vol)))" with no numpy import.

**Reality:** `verifier.py` does not generate prices or use numpy. No such code path exists. `crypto_api.py` uses hashlib only. Adversarial test uses `random.gauss`.

### abs(inv_norm) in UVRK

**Audit:** "predicted = θ * current + (1-θ) * κ * abs(inv_norm)"

**Reality:** `uvrk1_predict` uses raw `probit(rank)` with no abs(). Formula: `theta * current_vol + (1 - theta) * kappa * probit_rank`.

### realized_volatility with √(252×24)

**Audit:** Hourly volatility scaling in uvrk.py.

**Reality:** No `realized_volatility` function in uvrk.py. Engine uses stdlib only (math, no numpy). Backtest uses √252 (daily) consistently.

---

## Additional Fixes (Post-Audit v2)

| Item | Status |
|------|--------|
| Statistical significance (binomial test) | ✅ Added to backtest |
| Subperiod robustness (3 periods) | ✅ Added |
| Tail sensitivity (top 10% vol days) | ✅ Added (informational) |
| API input validation (1000 char limit) | ✅ Added |
| Collision claim language | ✅ Updated in olympic-report |
| Remove unused numpy import | ✅ Removed |

## Remaining Recommendations (Future Work)

| Item | Status |
|------|--------|
| Diebold–Mariano test | Noted |
| Oracle threshold out-of-sample | Noted |
| Rate limiting | Noted for production |
| CORS scope | Intentional; can restrict if needed |

---

## Conclusion

The audit correctly identified:
- Hardcoded fallback (fixed)
- Overstated 33 Voices claim (clarified)
- Missing input validation (added)

Several claims were not found in the current codebase. We documented volatility units and added an audit response for transparency.
