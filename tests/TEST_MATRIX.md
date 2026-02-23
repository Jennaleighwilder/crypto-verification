# Phase 0: Test Matrix — Battle Hardening Suite

## Run All Tests

```bash
cd ~/crypto-verification
source venv/bin/activate
python -m pytest tests/ -v --tb=short
```

---

## 1. Unit Tests — Every Component in Isolation

| Test | What It Checks | Status |
|------|----------------|--------|
| `test_uvrk_core.py` | Core equation, R², regime params | ✅ |
| `test_inverse_normal_cdf.py` | Φ⁻¹(p) accuracy within 0.1% | ✅ |
| `test_percentile_rank.py` | Rank calculation | ✅ |
| `test_realized_volatility.py` | Vol calculation | ✅ |
| `test_predict.py` | UVRK prediction | ✅ |
| `test_33_voices.py` | 33 Voices verification | ✅ |
| `test_voice_consistency.py` | Same input → same output | ✅ |
| `test_crypto_api.py` | Crypto API stub | ✅ |

---

## 2. Validation Tests — Against Historical Data

| Test | What It Checks | Target |
|------|----------------|--------|
| `validate_uvrk_bitcoin.py` | UVRK-1 on Bitcoin data | R² ≥ 0.95 (real) / sanity (synthetic) |
| `validate_outperformance.py` | vs Stoch Vol Lévy | ≥ +8.5σ |
| `validate_all_domains.py` | All 7 domains | Avg R² ≥ 0.94 |

**Note:** Replace `tests/data/bitcoin_daily_2015_2025.json` with real data for full validation.

---

## 3. Stress Tests — Try to Break It

| Test | What It Does | Status |
|------|--------------|--------|
| `stress_extreme_inputs.py` | Empty, 1M chars, emoji, binary, None | ✅ |
| `stress_concurrent_users.py` | 1000 simultaneous requests | ✅ |
| `stress_corrupt_data.py` | SQL injection, XSS, special chars | ✅ |

---

## 4. Adversarial Tests — Attack It

| Test | What It Does | Status |
|------|--------------|--------|
| `adversarial_33_voices.py` | 1000 random forgery attempts | ✅ 0% pass |

---

## 5. Benchmarks — Measure Everything

| Benchmark | Target | Status |
|-----------|--------|--------|
| `benchmark_uvrk_speed.py` | < 100ms per prediction | ✅ |
| `benchmark_33_voices.py` | < 500ms per verification | ✅ |
| `benchmark_concurrent.py` | > 100 req/sec | ✅ |

---

## What You Need to Provide

1. **Real Bitcoin data** — `tests/data/bitcoin_daily_2015_2025.json` with daily prices
2. **Stoch Vol Lévy** — Real implementation for `validate_outperformance` (currently uses EWMA proxy)
3. **33 Voices reference** — Real transforms for full adversarial coverage

---

## Interpret Results

| Result | Meaning | Action |
|--------|---------|--------|
| ✅ PASS | Component works | Move to next |
| ⚠️ WARNING | Works but below target | Tune parameters |
| ❌ FAIL | Broken | Fix immediately |
| 💥 CRASH | System died | Redesign |

**Then we deploy. Not before.**
