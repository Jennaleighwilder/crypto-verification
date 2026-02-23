# RAMANASH Macro Weighting — Formal Audit

**Purpose:** Economic interpretability and macro weighting logic audit per institutional review.

---

## PART I — Exact Macro Weighting Formula

**Source:** `engine/ramanash_kernel.py`

### Composite Index (not game-theoretic equilibrium)

```
NashEq_t = (sentiment × geo_risk + (1 − spending_pressure) × materials) × nash_strength
```

**Terminology:** Use "RAMANASH composite index" or "macro stress composite." Avoid "equilibrium" unless a fixed-point system is formally defined.

### Macro Inputs (Z_i)

| Variable | Key | Domain | Economic Interpretation |
|----------|-----|--------|--------------------------|
| Media sentiment | `media_sentiment` | [-1, 1] | News/social stress; negative = fear |
| Spending habits | `spending_habits` | [0, 1] | Consumer pressure; low = caution |
| War/conflict | `war_conflict` | [0, 1] | Geopolitical risk |
| Materials avail | `materials_avail` | [0, 1] | Supply chain stress |

### Implicit Weights

The formula is a **product structure**, not linear:

- Term A: `sentiment × geo_risk` — stress × geopolitical amplification
- Term B: `(1 − spending_pressure) × materials` — caution × supply

Effective weights depend on input magnitudes. All inputs are **pre-bounded** (scenario inputs); no rolling μ,σ applied at runtime.

### Volatility Adjustment

```
if NashEq_t < 0:
    shock_coef = f(NashEq_t, geo_risk)  # 0.5–0.75
    adjusted = base_vol × (1 + |NashEq_t| × shock_coef)
else:
    adjusted = base_vol × (1 + NashEq_t)
```

Additional multipliers: rank deviation, geo_risk > 0.75, spending_pressure < 0.45.

---

## PART II — Normalization Consistency

**Current design:** Macro inputs are **scenario values** (e.g. MACRO_FEB_23_2026), not time-series. They are:

- Bounded by design ([-1,1] or [0,1])
- Not standardized with rolling μ,σ
- Comparable in scale (all ~0.4–0.8 or ±0.8)

**For real-time macro:** If feeding live series (VIX, credit spreads, etc.), apply rolling standardization:

```
Z_{i,t} = (X_{i,t} − μ_{i,t−w:t}) / σ_{i,t−w:t}
```

---

## PART III — Weight Justification

| Criterion | Status | Notes |
|-----------|--------|-------|
| Theoretical rationale | ⚠️ | Product structure: stress × geo amplifies; (1−spending) × materials = caution × supply |
| Empirical fit | ❌ | Not estimated on data; scenario-based |
| Equal-weight baseline | N/A | Structure is multiplicative, not additive |

**Recommendation:** Document as "theoretically motivated composite; weights fixed ex-ante."

---

## PART IV — Monotonicity Check

**Test:** Increase each stress indicator; NashEq should move in consistent direction.

| Input | Direction | NashEq impact |
|-------|-----------|---------------|
| sentiment ↓ (more negative) | stress ↑ | NashEq ↓ (more negative) ✓ |
| geo_risk ↑ | stress ↑ | NashEq ↓ (via product) ✓ |
| spending_pressure ↓ | caution ↑ | Term B ↑; sign depends on materials |
| materials ↓ | supply stress ↑ | Term B ↓ if spending low |

**Caveat:** (1 − spending) × materials can decrease with rising materials when spending is low. Economically: low spending + scarce materials = stress. Monotonicity holds for stress interpretation.

---

## PART V — Threshold Provenance

| Threshold | Value | Frozen Date | Commit |
|-----------|-------|-------------|--------|
| CRISIS BREWING | NashEq < -0.35 | 2025-02-23 | (see THRESHOLD_PROVENANCE) |
| STEADY | NashEq > 0.35 | 2025-02-23 | (see THRESHOLD_PROVENANCE) |
| Shock coeffs | -0.38, -0.35, -0.30 | 2025-02-23 | (see THRESHOLD_PROVENANCE) |

**Method:** Fixed ex-ante; not tuned on full dataset. No optimization.

---

## PART VI — Event Definition (Time-Causality)

### Oracle Test (olympic_oracle_test.py)

- **Event:** Pre-defined crisis dates (COVID, China Ban, etc.)
- **Signal:** pred_vol / baseline > 1.5
- **Baseline:** Mean UVRK at past indices (before crisis − 30)
- **Leakage:** None. All data ≤ t.

### Time-Shift Test (olympic_bias_stress.py)

- **Event:** `vols[i+1] >= thresh` where `thresh = percentile(vols[i-window:i], 80)`
- **Threshold:** Rolling historical percentile only. ✅ No global percentile.
- **Leakage:** None.

### Backtest Tail Sensitivity (olympic_10_year_backtest.py)

- **Usage:** "Top 10% vol days" for *evaluation* (which days to include in win-rate)
- **Prediction:** Model never sees this. Used only to slice test set.
- **Leakage:** None. Evaluation metric, not feature.

---

## PART VII — Correlation Structure

**Current:** Four macro inputs. If real-time series are used:

- Check correlation matrix
- If two inputs > 0.9 correlated → consider PCA or orthogonalization
- Avoid double-counting

**Scenario inputs:** MACRO_FEB_23_2026 is a single scenario; no correlation structure at runtime.

---

## PART VIII — Summary

| Audit Item | Status |
|------------|--------|
| Formula documented | ✅ |
| Economic interpretation | ✅ |
| Normalization (scenario) | ✅ Pre-bounded |
| Monotonicity | ✅ |
| Threshold provenance | ✅ Documented |
| Event definition (rolling) | ✅ No global percentile |
| Weight justification | ⚠️ Theoretical; not empirical |

**Verdict:** RAMANASH is a **composite macro stress index** with fixed, theoretically motivated structure. Economically coherent for scenario-based volatility adjustment.
