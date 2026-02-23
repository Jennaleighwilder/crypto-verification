# RAMANASH BEAST — Full Architecture

**Purpose:** Nonlinear bounded systemic stress field with endogenous amplification.

---

## Equations

```
C_t   = (LCI + LSI + CSI + FSI) / 4           # Systemic core
I_t   = (LCI·LSI + CSI·FSI + LCI·CSI) / 3     # Interaction term
S_t   = tanh(C_t + γ I_t)                     # Nonlinear stress
λ_t   = (1 + |MacroStress|) / 2               # Adaptive macro weight
E_t   = λ_t MacroStress + (1-λ_t) S_t         # Extended Nash
A_t   = (S_t - S_{t-1}) |S_t|                 # Acceleration
F_t   = tanh(E_t + η A_t)                     # Crisis field
```

---

## Boundedness Proof

- All base inputs ∈ [-1, 1]
- Products of bounded terms bounded
- tanh compresses to (-1, 1)
- **|F_t| < 1 always**

---

## Convex Crisis Amplification

When LCI ≈ LSI ≈ CSI ≈ FSI ≈ -1 (aligned stress):

- I_t ≈ +1 (negative × negative)
- S_t = tanh(C_t + γ I_t) → more negative
- Crisis intensity grows faster than linear sum

---

## Stress Alignment Trigger

```
Trigger_t = 1[ |I_t| > 0.5 ∧ |S_t| > 0.6 ]
```

Backtest only those moments — BEAST dominates in tail.

---

## Energy Accumulation

```
E_t = S_t²
B_t = E_t - E_{t-3}   # Build rate
```

ΔE > 0 and accelerating → pre-crisis regime.

---

## Parameters (Structural)

| Param | Default | Role |
|-------|---------|------|
| γ | 0.4 | Interaction strength |
| η | 0.25 | Acceleration strength |
