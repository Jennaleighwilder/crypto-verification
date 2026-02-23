"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║              RAMANASH SYSTEMIC LAYER — Leverage, Liquidity, Credit, Funding   ║
║                                                                               ║
║  Extends RAMANASH with structural market stress indices.                      ║
║  No regression, no fitted weights, rolling-only, bounded.                    ║
║                                                                               ║
║  © 2025 Jennifer Leigh West • The Forgotten Code Research Institute           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import math
from typing import List, Optional, Tuple


def _bound(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _rolling_vol(prices: List[float], window: int, annualize: float = 252**0.5) -> List[float]:
    """Rolling realized vol from prices. Returns list aligned with prices[window:]."""
    returns = []
    for i in range(1, len(prices)):
        if prices[i - 1] > 0 and prices[i] > 0:
            returns.append(math.log(prices[i] / prices[i - 1]))
    vols = []
    for i in range(window, len(returns)):
        chunk = returns[i - window : i]
        mean = sum(chunk) / len(chunk)
        var = sum((x - mean) ** 2 for x in chunk) / len(chunk)
        vols.append(math.sqrt(var) * annualize)
    return vols


def _returns(prices: List[float]) -> List[float]:
    """Log returns."""
    out = []
    for i in range(1, len(prices)):
        if prices[i - 1] > 0 and prices[i] > 0:
            out.append(math.log(prices[i] / prices[i - 1]))
    return out


def leverage_cycle_index(
    prices: List[float],
    vols: List[float],
    i: int,
    vol_offset: int = 20,
    window_short: int = 7,
    window_long: int = 30,
) -> float:
    """
    LCI: structural leverage tension.
    (1 - v_l_norm) * m_norm + (v_s - v_l) interaction.
    Low long vol + momentum → buildup. Short vol > long vol → deleveraging.
    """
    if i < window_long or len(vols) < window_long or len(prices) < vol_offset + window_long + 1:
        return 0.0

    v_s = vols[min(i, len(vols) - 1)]
    hist_long = vols[max(0, i - window_long) : i]
    v_l = sum(hist_long) / len(hist_long) if hist_long else v_s

    # Momentum: P_t / P_{t-w} - 1. vols[i] aligns with prices[vol_offset+i]
    idx_now = vol_offset + i
    idx_prev = max(0, idx_now - window_long)
    if idx_now < len(prices) and prices[idx_prev] > 0 and prices[idx_now] > 0:
        mom_raw = prices[idx_now] / prices[idx_prev] - 1
        m = _bound(mom_raw * 5)
    else:
        m = 0.0

    # Normalize vols to [0,1] via rolling
    vol_hist = vols[max(0, i - 60) : i + 1]
    v_max = max(vol_hist) if vol_hist else 0.5
    v_min = min(vol_hist) if vol_hist else 0.01
    rng = v_max - v_min if v_max > v_min else 0.01
    v_s_norm = (v_s - v_min) / rng
    v_l_norm = (v_l - v_min) / rng

    term1 = (1 - v_l_norm) * m
    term2 = v_s_norm - v_l_norm
    lci = _bound(term1 + term2)
    return lci


def liquidity_spiral_index(
    prices: List[float],
    vols: List[float],
    vol_idx: int,
    ret_idx: Optional[int] = None,
    window_short: int = 7,
    window_jump: int = 5,
    vol_offset: int = 20,
) -> float:
    """
    LSI: j * |a| + (1 - p) * j.
    Jumps amplify acceleration; low participation amplifies jump stress.
    """
    if vol_idx < window_short or len(vols) < window_short or len(prices) < window_jump + 2:
        return 0.0

    r_idx = ret_idx if ret_idx is not None else vol_offset + vol_idx - 1
    v_s = vols[min(vol_idx, len(vols) - 1)]
    returns = _returns(prices)
    if len(returns) < r_idx + 1:
        return 0.0
    r_slice = returns[max(0, r_idx - window_jump) : r_idx + 1]
    if len(r_slice) < 2:
        return 0.0

    # Jump intensity: fraction of returns > 2x median abs
    abs_r = [abs(r) for r in r_slice]
    med = sorted(abs_r)[len(abs_r) // 2] if abs_r else 0.01
    thresh = 2.0 * med if med > 0 else 0.02
    jumps = [r for r in r_slice if abs(r) > thresh]
    j = len(jumps) / len(r_slice) if r_slice else 0
    j = _bound(j * 2)  # scale to [0,1]

    # Acceleration: |Δr| recent
    a = abs(r_slice[-1] - r_slice[-2]) if len(r_slice) >= 2 else 0
    a = _bound(a * 20)  # scale to [-1,1] for magnitude

    # Participation proxy: inverse of vol (high vol = low participation)
    vol_hist = vols[max(0, vol_idx - 30) : vol_idx + 1]
    p = 1 - (v_s / max(vol_hist)) if vol_hist and max(vol_hist) > 0 else 0.5
    p = _bound(p)

    # LSI = j * |a| + (1 - p) * j
    lsi = _bound(j * a + (1 - p) * j)
    return lsi


def credit_stress_index(
    returns: List[float],
    i: int,
    window: int = 30,
) -> float:
    """
    CSI: (d - u) * d. Downside pressure minus upside, weighted by downside.
    Strong convexity in downside.
    """
    if i < window or len(returns) < window:
        return 0.0

    r_slice = returns[max(0, i - window) : i + 1]
    downs = [r for r in r_slice if r < 0]
    ups = [r for r in r_slice if r >= 0]

    d_raw = math.sqrt(sum(r * r for r in downs) / len(downs)) if downs else 0
    u_raw = math.sqrt(sum(r * r for r in ups) / len(ups)) if ups else 0

    # Normalize to [0,1] via rolling
    all_sq = [r * r for r in r_slice]
    mx = max(all_sq) if all_sq else 0.01
    d = _bound(d_raw / (mx**0.5 + 0.01), 0, 1)
    u = _bound(u_raw / (mx**0.5 + 0.01), 0, 1)

    csi = _bound((d - u) * d)
    return csi


def funding_stress_index(
    vols: List[float],
    returns: List[float],
    vol_idx: int,
    ret_idx: Optional[int] = None,
    window_short: int = 7,
    window_long: int = 30,
) -> float:
    """
    FSI: Δv * |a|. Vol acceleration times price acceleration.
    """
    if vol_idx < window_long or len(vols) < window_long or len(returns) < 2:
        return 0.0
    r_idx = ret_idx if ret_idx is not None else vol_idx

    hist_s = vols[max(0, vol_idx - window_short) : vol_idx + 1]
    hist_l = vols[max(0, vol_idx - window_long) : vol_idx + 1]
    rv_7 = sum(hist_s) / len(hist_s) if hist_s else vols[vol_idx]
    rv_30 = sum(hist_l) / len(hist_l) if hist_l else vols[vol_idx]

    dv = rv_7 - rv_30
    r_slice = returns[max(0, r_idx - 3) : r_idx + 1]
    a = abs(r_slice[-1] - r_slice[-2]) if len(r_slice) >= 2 else 0

    dv_norm = _bound(dv * 5)
    a_norm = _bound(a * 20)
    fsi = _bound(dv_norm * a_norm)
    return fsi


def systemic_stress(
    prices: List[float],
    vols: List[float],
    i: int,
    vol_offset: int = 20,
) -> float:
    """
    SystemicStress = (LCI + LSI + CSI + FSI) / 4.
    Equal weights. Bounded [-1, 1].
    i = vol index (vols[i] aligns with prices[vol_offset+i]).
    """
    returns = _returns(prices)
    vol_idx = min(i, len(vols) - 1)
    ret_idx = min(vol_offset + i - 1, len(returns) - 1) if vol_offset + i > 0 else 0

    lci = leverage_cycle_index(prices, vols, vol_idx, vol_offset=vol_offset)
    lsi = liquidity_spiral_index(prices, vols, vol_idx, ret_idx=ret_idx, vol_offset=vol_offset)
    csi = credit_stress_index(returns, ret_idx)
    fsi = funding_stress_index(vols, returns, vol_idx, ret_idx=ret_idx)

    systemic = (lci + lsi + csi + fsi) / 4
    return _bound(systemic)


def systemic_stress_full(
    prices: List[float],
    vols: List[float],
    i: int,
    vol_offset: int = 20,
) -> dict:
    """Return all four indices plus combined systemic stress."""
    returns = _returns(prices)
    vol_idx = min(i, len(vols) - 1)
    ret_idx = min(vol_offset + i - 1, len(returns) - 1) if vol_offset + i > 0 else 0

    lci = leverage_cycle_index(prices, vols, vol_idx, vol_offset=vol_offset)
    lsi = liquidity_spiral_index(prices, vols, vol_idx, ret_idx=ret_idx, vol_offset=vol_offset)
    csi = credit_stress_index(returns, ret_idx)
    fsi = funding_stress_index(vols, returns, vol_idx, ret_idx=ret_idx)
    systemic = _bound((lci + lsi + csi + fsi) / 4)

    return {
        "lci": lci,
        "lsi": lsi,
        "csi": csi,
        "fsi": fsi,
        "systemic_stress": systemic,
    }
