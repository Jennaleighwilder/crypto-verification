# Dominance Proof — Performance & Structural

**Purpose:** Prove BEAST structural superiority via dominance battery, phase diagram, cross-asset validation.

---

## PART I — Performance Dominance Battery

**`tests/olympic_dominance_battery.py`**

| Test | Condition | Interpretation |
|------|-----------|----------------|
| **Decile Monotonicity** | M ≥ 0.6 (0.8 strict) | F_t deciles → monotonic future vol ordering |
| **Convex Tail Ratio** | CTR > 1.2 (1.5 strict) | E[vol\|high \|F\|] / E[vol\|low \|F\|] |
| **Acceleration Energy** | E[vol\|Accel>0.2] > E[vol\|Accel<0] | Second-derivative detection |
| **Interaction Alignment** | vol(high \|I\|) > vol(low \|I\|) | Systemic alignment amplifies |
| **Regime Elasticity** | Dynamic CTR ≥ Static CTR | Adaptive λ dominance |
| **Parameter Stability** | Drop < 10% when γ,η ±20% | Structural, not curve-fit |

**Run:** `python tests/olympic_dominance_battery.py` (relaxed) or `--strict` (blueprint)

---

## PART II — Phase Diagram

**`analysis/phase_diagram.py`**

- **Crisis Intensity:** CI(γ,η) = E[|F_t|]
- **Tail Frequency:** P(|F_t| > 0.8)
- **Critical γ:** Smallest γ such that P(|F_t|>0.8) > 5%
- **Stability:** ρ + |β| < 1 (dynamical engine)

---

## PART III — Cross-Asset Validation

**`tests/olympic_cross_asset.py`**

- **Assets:** BTC, ETH, SOL, SPX, Gold (load from `tests/data/*.json`)
- **No parameter changes.** No retraining.
- **Structural portability:** M ≥ 0.6, CTR ≥ 1.0 on at least one asset

---

## Run

```bash
python tests/olympic_dominance_battery.py
python analysis/phase_diagram.py
python tests/olympic_cross_asset.py
```
