# RAMANASH Dynamical Engine

**Purpose:** Bounded nonlinear recursive systemic stress with convex tail amplification.

---

## Equations

```
Oracle_t     = tanh(UVRK_norm + ExtendedNashEq)
S_t          = ρ S_{t-1} + (1−ρ) Oracle_t + β (UVRK_norm · S_{t-1})
ShockAmp_t   = S_t |S_t|
SystemIndex_t = tanh(S_t + α ShockAmp_t)
```

---

## Stability Condition

**ρ + |β| < 1**

Default: ρ=0.85, β=0.08 → 0.93 < 1 ✓

Guarantees: bounded attractor, no explosion, no divergence.

---

## Properties

| Property | Status |
|----------|--------|
| Boundedness | All state ∈ [-1, 1] |
| Determinism | No randomness |
| Convex amplification | ShockAmp = S\|S\| |
| Feedback | Vol-stress coupling via β term |
| Tail convexity | \|S\|→1 ⇒ SystemIndex → tanh((1+α)S) |

---

## Energy Function

E_t = S_t²  
ΔE_t = E_t − E_{t-1}

When ΔE > 0 and accelerating → pre-crisis regime.

---

## Parameters (Structural, Not Fitted)

| Param | Default | Role |
|-------|---------|------|
| ρ | 0.85 | State memory persistence |
| β | 0.08 | Volatility-stress feedback |
| α | 0.30 | Convex shock strength |
