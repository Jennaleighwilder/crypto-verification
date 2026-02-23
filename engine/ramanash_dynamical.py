"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║         RAMANASH DYNAMICAL ENGINE — Bounded Nonlinear Recursive Stress         ║
║                                                                               ║
║  State memory + convex shock amplification + volatility-stress feedback.        ║
║  Stability: ρ + |β| < 1. Provably non-explosive.                              ║
║                                                                               ║
║  © 2025 Jennifer Leigh West • The Forgotten Code Research Institute           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import math
from typing import List, Optional, Dict, Any

# Stability condition: ρ + |β| < 1. Defaults satisfy this.
RHO_DEFAULT = 0.85   # State memory persistence
BETA_DEFAULT = 0.08  # Volatility-stress feedback
ALPHA_DEFAULT = 0.3  # Convex shock amplification


def _tanh(x: float) -> float:
    return math.tanh(x)


def _uvrk_norm(vol: float, vol_history: List[float]) -> float:
    """Normalize vol to [-1,1] via rolling percentile. High vol → high stress."""
    if not vol_history:
        return 0.0
    below = sum(1 for v in vol_history if v < vol)
    rank = below / len(vol_history)
    rank = max(0.001, min(0.999, rank))
    # rank 0 → -1, rank 1 → 1. probit(rank) then tanh for smooth bound
    from engine.uvrk import probit
    z = probit(rank)
    return _tanh(z / 2)  # scale to [-1,1]


def dynamical_step(
    oracle_raw: float,
    uvrk_norm: float,
    s_prev: float,
    rho: float = RHO_DEFAULT,
    beta: float = BETA_DEFAULT,
    alpha: float = ALPHA_DEFAULT,
) -> Dict[str, float]:
    """
    One step of the dynamical system.

    Oracle_t = tanh(oracle_raw)  [caller provides oracle_raw = UVRK_norm + ExtendedNashEq]
    S_t = ρ S_{t-1} + (1-ρ) Oracle_t + β (UVRK_norm · S_{t-1})
    ShockAmplifier_t = S_t |S_t|
    SystemIndex_t = tanh(S_t + α ShockAmplifier_t)

    Stability: ρ + |β| < 1.
    """
    oracle_t = _tanh(oracle_raw)
    s_t = rho * s_prev + (1 - rho) * oracle_t + beta * (uvrk_norm * s_prev)
    s_t = max(-1.0, min(1.0, s_t))

    shock_amp = s_t * abs(s_t)
    system_index = _tanh(s_t + alpha * shock_amp)

    e_t = s_t * s_t
    return {
        "oracle": oracle_t,
        "state": s_t,
        "shock_amplifier": shock_amp,
        "system_index": system_index,
        "energy": e_t,
    }


def run_dynamical(
    uvrk_norms: List[float],
    extended_nash_eqs: List[float],
    rho: float = RHO_DEFAULT,
    beta: float = BETA_DEFAULT,
    alpha: float = ALPHA_DEFAULT,
    s_init: float = 0.0,
) -> List[Dict[str, float]]:
    """
    Run full dynamical system over time series.
    oracle_raw_t = uvrk_norms[t] + extended_nash_eqs[t]
    """
    assert rho + abs(beta) < 1, f"Stability violated: ρ+|β|={rho + abs(beta):.3f} >= 1"
    n = min(len(uvrk_norms), len(extended_nash_eqs))
    out = []
    s = s_init
    e_prev = s_init * s_init

    for t in range(n):
        oracle_raw = uvrk_norms[t] + extended_nash_eqs[t]
        step = dynamical_step(
            oracle_raw, uvrk_norms[t], s,
            rho=rho, beta=beta, alpha=alpha,
        )
        step["delta_energy"] = step["energy"] - e_prev
        e_prev = step["energy"]
        s = step["state"]
        out.append(step)

    return out


def dynamical_from_market(
    prices: List[float],
    vols: List[float],
    macro_factors: Dict[str, Any],
    vol_offset: int = 20,
    rho: float = RHO_DEFAULT,
    beta: float = BETA_DEFAULT,
    alpha: float = ALPHA_DEFAULT,
) -> List[Dict[str, Any]]:
    """
    Build dynamical system from market data.
    Uses predict_macro_systemic when prices/vols available, else macro-only.
    """
    from engine.ramanash_kernel import predict_macro_systemic

    uvrk_norms = []
    extended_nash_eqs = []

    for i in range(vol_offset + 30, len(vols) - 1):
        vol = vols[i]
        hist = vols[max(0, i - 60) : i + 1]
        uvrk_n = _uvrk_norm(vol, hist)

        if i + vol_offset < len(prices):
            r = predict_macro_systemic(
                0.04, macro_factors,
                prices=prices, vols=vols, vol_idx=i,
                vol_offset=vol_offset,
            )
        else:
            r = predict_macro_systemic(0.04, macro_factors)

        uvrk_norms.append(uvrk_n)
        extended_nash_eqs.append(r["nash_eq"])

    return run_dynamical(uvrk_norms, extended_nash_eqs, rho=rho, beta=beta, alpha=alpha)


def pre_crisis_signal(steps: List[Dict[str, float]], window: int = 5) -> bool:
    """
    ΔE positive and accelerating → pre-crisis regime.
    Returns True if recent delta_energy is positive and increasing.
    """
    if len(steps) < window + 1:
        return False
    de = [s.get("delta_energy", 0) for s in steps[-window:]]
    if not all(d > 0 for d in de):
        return False
    # Accelerating: de[-1] > de[-2] > ...
    for i in range(1, len(de)):
        if de[i] <= de[i - 1]:
            return False
    return True
