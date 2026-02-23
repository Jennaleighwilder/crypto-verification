# Battle Hardening Suite

## Test Matrix

### 1. Unit Tests
| Test | What It Checks |
|------|----------------|
| `test_uvrk_core.py` | Core equation, R², regime params |
| `test_inverse_normal_cdf.py` | Φ⁻¹(p) accuracy |
| `test_percentile_rank.py` | Rank calculation |
| `test_realized_volatility.py` | Vol calculation |
| `test_predict.py` | UVRK prediction |
| `test_33_voices.py` | 33 Voices verification |
| `test_voice_consistency.py` | Determinism |
| `test_crypto_api.py` | Crypto API stub |

### 2. Validation Tests
| Test | Target |
|------|--------|
| `validate_uvrk_bitcoin.py` | R² ≥ 0.5 (synthetic) / 0.95 (real data) |
| `validate_outperformance.py` | Outperformance vs Stoch Vol Lévy |
| `validate_all_domains.py` | Avg R² ≥ 0.94 |

### 3. Stress Tests
| Test | Expected |
|------|----------|
| `stress_extreme_inputs.py` | No crash on garbage |
| `stress_concurrent_users.py` | 1000 requests, < 2s each |
| `stress_corrupt_data.py` | Validation fails, not crash |

### 4. Adversarial Tests
| Test | Target |
|------|--------|
| `adversarial_33_voices.py` | 0% forgery rate |

### 5. Benchmarks
| Benchmark | Target |
|-----------|--------|
| `benchmark_uvrk_speed.py` | < 100ms per prediction |
| `benchmark_33_voices.py` | < 500ms per verification |
| `benchmark_concurrent.py` | > 100 req/sec |

## Run All Tests

```bash
cd ~/crypto-verification
source venv/bin/activate
pip install pytest scipy  # scipy optional for probit accuracy
python -m pytest tests/ -v --tb=short
```

## Provide Real Data

Replace `tests/data/bitcoin_daily_2015_2025.json` with your actual Bitcoin daily prices:

```json
{
  "prices": [400, 401.2, ...],
  "volatilities": [],
  "source": "yfinance",
  "note": "BTC-USD daily close 2015-2025"
}
```

Or use yfinance to fetch:

```python
import yfinance as yf
import json
data = yf.download("BTC-USD", start="2015-01-01", end="2025-01-01", progress=False)
prices = data['Close'].tolist()
```
