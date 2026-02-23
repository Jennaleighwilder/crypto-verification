# RAMANASH Systemic Layer

**Purpose:** Extend RAMANASH with structural market stress indices — leverage, liquidity, credit, funding.

---

## Architecture

```
ExtendedNashEq = λ × MacroStress + (1 − λ) × SystemicStress
SystemicStress = (LCI + LSI + CSI + FSI) / 4
```

All components: **bounded, rolling-only, no regression, no fitted weights.**

---

## Indices

| Index | Formula | Interpretation |
|-------|---------|----------------|
| **LCI** | (1−v_l)×m + (v_s−v_l) | Leverage cycle: low long vol + momentum → buildup; short > long → deleveraging |
| **LSI** | j×\|a\| + (1−p)×j | Liquidity spiral: jumps × acceleration; low participation amplifies |
| **CSI** | (d−u)×d | Credit stress: downside convexity |
| **FSI** | Δv × \|a\| | Funding stress: vol acceleration × price acceleration |

---

## Usage

**Full systemic (backtest, Olympic):**
```python
from engine.ramanash_kernel import predict_macro_systemic
r = predict_macro_systemic(0.04, MACRO_FEB_23_2026, prices=prices, vols=vols, vol_idx=i)
# r["nash_eq"], r["systemic_stress"], r["lci"], r["lsi"], r["csi"], r["fsi"]
```

**Macro-only (API, no price history):**
```python
r = predict_macro_systemic(0.04, MACRO_FEB_23_2026)
# Falls back to MacroStress only
```

---

## Bias Safety

- Rolling windows only
- No global normalization
- No future information
- Equal weights (1/4 each)
- λ = 0.5 default
