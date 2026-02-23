# Nash + Oracle Rigorous Audit

**Purpose:** Institutional-grade audit of forward-looking bias risk for RAMANASH-ORACLE and UVRK-1.

---

## PART I — Exact Mathematical Definitions

### 1. Nash Layer (RAMANASH Kernel)

**Source:** `engine/ramanash_kernel.py`

#### NashEq_t (signed scalar)

```
NashEq_t = (sentiment × geo_risk + (1 − spending_pressure) × materials) × nash_strength
```

Where:
- `sentiment` = media_sentiment ∈ [-1, 1]
- `geo_risk` = war_conflict ∈ [0, 1]
- `spending_pressure` = spending_habits ∈ [0, 1]
- `materials` = materials_avail ∈ [0, 1]
- `nash_strength` = scalar (default 0.25, stress-test 1.25)

**Interpretation:** Weighted combination of macro factors. The "Nash" is narrative—it is not a game-theoretic equilibrium.

**Determinism:** ✅ Same inputs → same output. No randomness.

#### Nash Confidence (should be renamed: Nash Score)

```
nash_confidence = 0.70 + 0.30 × |NashEq_t|
if geo_risk ≥ 0.75: nash_confidence = min(0.99, nash_confidence + 0.05)
```

**Calibration:** ❌ NOT calibrated. P(event|conf≈0.85) ≠ 0.85. **Implemented:** API returns both `nash_confidence` (backward compat) and `nash_score` (institutional term).

#### CRISIS BREWING Threshold

```
CRISIS_t = 1  if NashEq_t < -0.35
STEADY_t = 1  if NashEq_t > 0.35
NEUTRAL   otherwise
```

**Threshold provenance:** Frozen 2025-02-23. See `docs/THRESHOLD_PROVENANCE.md` and `engine/ramanash_kernel.py` constants.

---

### 2. Oracle Layer (UVRK-1 + Olympic Oracle Test)

**Source:** `engine/uvrk.py`, `tests/olympic_10_year_backtest.py`, `tests/olympic_oracle_test.py`

#### UVRK-1 Core Formula

```
V_{t+1} = θ × V_t + (1−θ) × κ × Φ⁻¹(rank_t) + ε_t
```

Where:
- `rank_t` = percentile rank of V_t in rolling history (window ≤ 252)
- `rank_t = compute_rank(V_t, history[max(0,t−window):t], window)`
- `history` = rolling realized vol from prices ≤ t

**Time-causality:** ✅ rank uses only data ≤ t.

#### Oracle Event Definition (Olympic Test)

- **Event:** Crisis date (pre-defined: COVID, China Ban, Celsius, etc.)
- **Prediction:** `pred_vol / baseline > 1.5` → PREDICTED
- **baseline:** Mean of UVRK predictions at random past indices (before crisis − 30)
- **Data:** `price_slice = prices[: 20 + vol_idx + 1]` — only past data

**Time-causality:** ✅ Uses only past prices.

---

### 3. Rolling vs Global Statistics

| Component | Statistic | Window | Time-causal? |
|-----------|-----------|--------|--------------|
| `_rolling_volatility` | mean, var | 20 | ✅ |
| `compute_rank` | percentile | rolling (≤252) | ✅ |
| `_detect_regime` | mean, std, rank | rolling (≤60) | ✅ |
| `_uvrk_predict` vol_mean | expanding | vols[:i] | ✅ (no future) |
| `_uvrk_predict` vol_std | expanding | vols[:i] | ✅ (no future) |
| Tail sensitivity (backtest) | "top 10%" | full sample | ⚠️ Evaluation only |

**Note:** Tail sensitivity in backtest uses global percentile for *evaluation* (which days were high-vol). The *prediction* never sees that. No leakage.

---

## PART II — Audit Checklist

### Nash Layer

| Check | Status | Notes |
|------|--------|-------|
| Determinism | ✅ | No randomness |
| Well-posedness | ✅ | Always converges (closed-form) |
| NashEq interpretation | ⚠️ | Document as signed macro imbalance |
| Nash confidence calibration | ❌ | Rename to Nash Score |
| Threshold provenance | ✅ | Hardcoded, not data-tuned |

### Oracle Layer

| Check | Status | Notes |
|------|--------|-------|
| Time-causality | ✅ | Rolling only |
| No global percentiles in prediction | ✅ | `compute_rank` uses rolling |
| No global normalization in prediction | ✅ | Expanding mean/std (past only) |
| Event definition | ✅ | Rolling/baseline |

### Macro Inputs

| Check | Status | Notes |
|------|--------|-------|
| Revision-safe | ⚠️ | MACRO_FEB_23_2026 is scenario; not real-time |
| Sensitivity test | Pending | Add lag/noise robustness |

---

## PART III — Pass/Fail Criteria for Stress Tests

1. **Purged walk-forward:** G ≥ 90 (longest lookback). Performance should not collapse.
2. **Rolling vs global A/B:** Forced rolling-only; win rate drop < 10% acceptable.
3. **Time-shift test:** Oracle(t+1) must NOT outperform Oracle(t).
4. **Nash calibration:** ECE < 0.10 or rename to Nash Score.

---

## PART IV — Recommendation

- **Nash confidence:** Rename to `nash_score` in API/docs until calibration is proven.
- **Thresholds:** Document -0.35 / 0.35 as pre-registered (no tuning). See `docs/THRESHOLD_PROVENANCE.md`.
- **Run stress tests:** Run `tests/olympic_bias_stress.py` before institutional review.
- **Event definition:** Time-shift test uses rolling percentile only. Oracle test uses pre-defined crisis dates. No global percentile leakage.
