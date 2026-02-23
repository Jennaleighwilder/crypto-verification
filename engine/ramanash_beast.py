"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║         RAMANASH BEAST — Nonlinear Bounded Systemic Stress Field              ║
║                                                                               ║
║  Interaction term + adaptive macro + acceleration + crisis field.             ║
║  Provably bounded. Convex crisis amplification. Phase-sensitive.              ║
║                                                                               ║
║  © 2025 Jennifer Leigh West • The Forgotten Code Research Institute           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import math
from typing import List, Dict, Any, Optional

# Structural parameters (not fitted)
GAMMA_DEFAULT = 0.4   # Interaction strength
ETA_DEFAULT = 0.25    # Acceleration strength


def _tanh(x: float) -> float:
    return math.tanh(x)


def _bound(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def beast_step(
    lci: float,
    lsi: float,
    csi: float,
    fsi: float,
    macro_stress: float,
    s_prev: float = 0.0,
    gamma: float = GAMMA_DEFAULT,
    eta: float = ETA_DEFAULT,
    static_lambda: Optional[float] = None,
) -> Dict[str, float]:
    """
    One step of BEAST core.

    C_t = (LCI + LSI + CSI + FSI) / 4
    I_t = (LCI·LSI + CSI·FSI + LCI·CSI) / 3
    S_t = tanh(C_t + γ I_t)
    λ_t = (1 + |MacroStress|) / 2
    E_t = λ_t MacroStress + (1-λ_t) S_t
    A_t = (S_t - S_{t-1}) |S_t|
    F_t = tanh(E_t + η A_t)

    All bounded. No explosion.
    """
    lci, lsi, csi, fsi = _bound(lci), _bound(lsi), _bound(csi), _bound(fsi)
    macro_stress = _bound(macro_stress)

    # Systemic core
    c_t = (lci + lsi + csi + fsi) / 4

    # Interaction term (convex when aligned)
    i_t = (lci * lsi + csi * fsi + lci * csi) / 3

    # Nonlinear stress
    s_t = _tanh(c_t + gamma * i_t)

    # Macro weight: adaptive or static
    lam_t = static_lambda if static_lambda is not None else (1 + abs(macro_stress)) / 2

    # Extended Nash
    e_t = lam_t * macro_stress + (1 - lam_t) * s_t
    e_t = _bound(e_t)

    # Acceleration
    a_t = (s_t - s_prev) * abs(s_t)
    a_t = _bound(a_t)

    # Final crisis field
    f_t = _tanh(e_t + eta * a_t)

    # Energy
    energy = s_t * s_t

    # Aligned stress magnitude
    m_t = (abs(lci) + abs(lsi) + abs(csi) + abs(fsi)) / 4

    # Stress alignment trigger
    trigger = 1 if (abs(i_t) > 0.5 and abs(s_t) > 0.6) else 0

    return {
        "core": c_t,
        "interaction": i_t,
        "stress": s_t,
        "lambda_t": lam_t,
        "extended_nash": e_t,
        "acceleration": a_t,
        "crisis_field": f_t,
        "energy": energy,
        "aligned_magnitude": m_t,
        "trigger": trigger,
    }


def beast_run(
    lci_list: List[float],
    lsi_list: List[float],
    csi_list: List[float],
    fsi_list: List[float],
    macro_stress_list: List[float],
    gamma: float = GAMMA_DEFAULT,
    eta: float = ETA_DEFAULT,
    s_init: float = 0.0,
    static_lambda: Optional[float] = None,
) -> List[Dict[str, float]]:
    """Run BEAST over time series."""
    n = min(len(lci_list), len(lsi_list), len(csi_list), len(fsi_list), len(macro_stress_list))
    out = []
    s_prev = s_init
    e_prev = s_init * s_init

    e_init = s_init * s_init
    for t in range(n):
        step = beast_step(
            lci_list[t], lsi_list[t], csi_list[t], fsi_list[t],
            macro_stress_list[t], s_prev=s_prev, gamma=gamma, eta=eta,
            static_lambda=static_lambda,
        )
        step["delta_energy"] = step["energy"] - e_prev
        step["build_rate"] = step["energy"] - (out[t - 3]["energy"] if t >= 3 else e_init)
        s_prev = step["stress"]
        e_prev = step["energy"]
        out.append(step)

    return out


def beast_from_market(
    prices: List[float],
    vols: List[float],
    macro_factors: Dict[str, Any],
    vol_offset: int = 20,
    gamma: float = GAMMA_DEFAULT,
    eta: float = ETA_DEFAULT,
    static_lambda: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """Build BEAST from market data. Uses systemic layer + macro."""
    from engine.ramanash_systemic import systemic_stress_full
    from engine.ramanash_kernel import predict_macro

    lci_list, lsi_list, csi_list, fsi_list = [], [], [], []
    macro_stress_list = []

    for i in range(vol_offset + 30, len(vols) - 1):
        s = systemic_stress_full(prices, vols, i, vol_offset)
        m = predict_macro(0.04, macro_factors)
        macro_stress = m["nash_eq"]

        lci_list.append(s["lci"])
        lsi_list.append(s["lsi"])
        csi_list.append(s["csi"])
        fsi_list.append(s["fsi"])
        macro_stress_list.append(macro_stress)

    return beast_run(lci_list, lsi_list, csi_list, fsi_list, macro_stress_list, gamma=gamma, eta=eta, static_lambda=static_lambda)


def stress_alignment_trigger(step: Dict[str, float], i_thresh: float = 0.5, s_thresh: float = 0.6) -> bool:
    """Crisis trigger: |I_t| > i_thresh ∧ |S_t| > s_thresh."""
    return bool(step.get("trigger", 0))


def tail_lift(
    beast_steps: List[Dict[str, float]],
    future_vols: List[float],
    baseline_vol: float,
    f_thresh: float = -0.7,
) -> float:
    """
    Lift_tail = (mean future vol when F_t < f_thresh) / baseline - 1
    Performance dominance: tail capture.
    """
    if len(beast_steps) != len(future_vols) or baseline_vol <= 0:
        return 0.0
    tail_vols = [future_vols[t] for t in range(len(beast_steps)) if beast_steps[t].get("crisis_field", 0) < f_thresh]
    if not tail_vols:
        return 0.0
    return (sum(tail_vols) / len(tail_vols)) / baseline_vol - 1.0
