"""
Phase Diagram & Bifurcation Analysis

Varies γ, η over [0,1]. Computes:
- Mean |F_t|
- Tail frequency P(|F_t| > 0.8)
- Stability (variance of S_t)
- Critical γ threshold
"""
import sys
import os
import json
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.ramanash_beast import beast_from_market, beast_run
from engine.ramanash_systemic import systemic_stress_full
from engine.ramanash_kernel import predict_macro


def _synthetic_stress(n=500, seed=42):
    """Synthetic stress series for phase sweep."""
    import random
    r = random.Random(seed)
    return [max(-1, min(1, r.gauss(0, 0.4))) for _ in range(n)]


def run_phase_sweep(gamma_vals, eta_vals, data_path=None):
    """
    Sweep γ × η. Return dict: (γ, η) -> {mean_abs_f, tail_freq, var_s}.
    """
    if data_path and os.path.exists(data_path):
        with open(data_path) as f:
            data = json.load(f)
        from tests.olympic_10_year_backtest import _rolling_volatility
        prices = data['prices']
        vols = _rolling_volatility(prices, window=20)
        macro = {"media_sentiment": -0.5, "spending_habits": 0.5, "war_conflict": 0.5, "materials_avail": 0.5}
        steps_source = beast_from_market(prices, vols, macro)
        n = len(steps_source)
        lci_list = _synthetic_stress(n, 42)
        lsi_list = _synthetic_stress(n, 43)
        csi_list = _synthetic_stress(n, 44)
        fsi_list = _synthetic_stress(n, 45)
        macro_list = [-0.1] * n
    else:
        n = 300
        lci_list = _synthetic_stress(n, 42)
        lsi_list = _synthetic_stress(n, 43)
        csi_list = _synthetic_stress(n, 44)
        fsi_list = _synthetic_stress(n, 45)
        macro_list = [-0.2] * n

    results = {}
    for gamma in gamma_vals:
        for eta in eta_vals:
            steps = beast_run(lci_list, lsi_list, csi_list, fsi_list, macro_list, gamma=gamma, eta=eta)
            abs_f = [abs(s["crisis_field"]) for s in steps]
            tail_count = sum(1 for f in abs_f if f > 0.8)
            var_s = 0
            if len(steps) > 1:
                stresses = [s["stress"] for s in steps]
                mean_s = sum(stresses) / len(stresses)
                var_s = sum((x - mean_s) ** 2 for x in stresses) / len(stresses)
            results[(gamma, eta)] = {
                "mean_abs_f": sum(abs_f) / len(abs_f) if abs_f else 0,
                "tail_freq": tail_count / len(steps) if steps else 0,
                "var_s": var_s,
            }
    return results


def critical_gamma(eta=0.25, tail_thresh=0.05, n_points=20):
    """Find smallest γ such that P(|F_t| > 0.8) > tail_thresh."""
    gamma_vals = [i / n_points for i in range(1, n_points + 1)]
    for gamma in gamma_vals:
        res = run_phase_sweep([gamma], [eta])
        v = res.get((gamma, eta), {})
        tf = v.get("tail_freq", 0)
        if tf > tail_thresh:
            return gamma
    return None


def main():
    print("Phase Diagram & Bifurcation Analysis")
    print("=" * 50)

    gamma_vals = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    eta_vals = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

    data_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'data', 'bitcoin_daily_2015_2025.json')
    results = run_phase_sweep(gamma_vals, eta_vals, data_path)

    print("\nCrisis Intensity CI(γ,η) = E[|F_t|]:")
    print("γ \\ η  ", "  ".join(f"{e:5.2f}" for e in eta_vals))
    for gamma in gamma_vals:
        row = f"{gamma:5.2f} "
        for eta in eta_vals:
            v = results.get((gamma, eta), {}).get("mean_abs_f", 0)
            row += f" {v:.3f}"
        print(row)

    print("\nTail Frequency P(|F_t|>0.8):")
    print("γ \\ η  ", "  ".join(f"{e:5.2f}" for e in eta_vals))
    for gamma in gamma_vals:
        row = f"{gamma:5.2f} "
        for eta in eta_vals:
            v = results.get((gamma, eta), {}).get("tail_freq", 0)
            row += f" {v:.3f}"
        print(row)

    gamma_crit = critical_gamma(eta=0.25, tail_thresh=0.05)
    print(f"\nCritical γ (P(|F|>0.8)>5% at η=0.25): {gamma_crit:.2f}" if gamma_crit else "\nCritical γ: not reached in [0.05,1]")

    print("\n✅ Phase diagram complete")


if __name__ == "__main__":
    main()
