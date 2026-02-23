"""
🏅 OLYMPIC: 10-Year Backtest — UVRK-1 vs every benchmark on every day

Volatility units: All models use daily log returns, annualized with √252.
_rolling_volatility, _stoch_vol_levy, _uvrk_predict all operate in same units.
"""
import sys
import os
import math
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.uvrk import REGIMES, probit, compute_rank

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


def _rolling_volatility(prices, window=20):
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] > 0 and prices[i] > 0:
            returns.append(math.log(prices[i] / prices[i-1]))
    vols = []
    for i in range(window, len(returns)):
        chunk = returns[i-window:i]
        mean = sum(chunk) / len(chunk)
        var = sum((x - mean)**2 for x in chunk) / len(chunk)
        vols.append(math.sqrt(var) * math.sqrt(252))
    return vols


# Regime-gated parameters (tail = high-vol days)
THETA_NORMAL = REGIMES['bitcoin']['theta']
KAPPA_NORMAL = REGIMES['bitcoin']['kappa']
THETA_TAIL = 0.75   # Lower = faster adaptation in tails
KAPPA_TAIL = 0.35   # Higher = stronger shock response
JUMP_LAMBDA = 0.25  # Jump component strength in tails


def _detect_regime(vols, i, window=60):
    """Detect if current vol is in tail (top 10%) or normal regime."""
    if i < 10:
        return {'regime': 'normal', 'rank': 0.5, 'z_score': 0.0, 'is_tail': False}
    history = vols[max(0, i - window) : i + 1]
    v_t = vols[i]
    rank = compute_rank(v_t, history, window=len(history))
    mean_vol = sum(history) / len(history)
    var_vol = sum((v - mean_vol) ** 2 for v in history) / len(history)
    std_vol = math.sqrt(var_vol) if var_vol > 0 else 0.01
    z_score = (v_t - mean_vol) / std_vol if std_vol > 0 else 0.0
    is_tail = (rank > 0.90) or (z_score > 1.5)
    return {'regime': 'tail' if is_tail else 'normal', 'rank': rank, 'z_score': z_score, 'is_tail': is_tail}


def _calculate_jump(prices, window=14):
    """Jump risk from recent returns — returns above 2x median absolute."""
    if len(prices) < window + 1:
        return 0.0
    returns = []
    for i in range(1, min(window + 1, len(prices))):
        if prices[-(i + 1)] > 0 and prices[-i] > 0:
            r = (prices[-i] - prices[-(i + 1)]) / prices[-(i + 1)]
            if abs(r) < 0.5:  # filter outliers
                returns.append(abs(r))
    if len(returns) < 3:
        return 0.0
    sorted_abs = sorted(returns)
    median_abs = sorted_abs[len(sorted_abs) // 2]
    threshold = 2.0 * median_abs if median_abs > 0 else 0.02
    jumps = [r for r in returns if r > threshold]
    return sum(jumps) / len(jumps) if jumps else 0.0


def _uvrk_predict(vols, i, window=60, prices=None, vol_window=20):
    """UVRK-1 prediction with regime gating — faster adaptation in tail regimes."""
    params = REGIMES['bitcoin']
    vol_mean = sum(vols[:i]) / i if i > 0 else 0.04
    vol_std = math.sqrt(sum((v - vol_mean) ** 2 for v in vols[:i]) / i) or 0.01 if i > 0 else 0.01
    v_t = vols[i]
    history = vols[max(0, i - window) : i]
    rank = compute_rank(v_t, history, window=min(window, len(history)))

    regime_info = _detect_regime(vols, i, window)
    theta = THETA_TAIL if regime_info['is_tail'] else THETA_NORMAL
    kappa = KAPPA_TAIL if regime_info['is_tail'] else KAPPA_NORMAL

    pred = theta * v_t + (1 - theta) * vol_mean + kappa * vol_std * probit(rank)

    # Jump component in tail regime
    if regime_info['is_tail'] and prices and len(prices) >= 15:
        price_slice = prices[max(0, len(prices) - 30) :]
        jump = _calculate_jump(price_slice, window=14)
        if jump > 0:
            pred += JUMP_LAMBDA * jump * v_t

    return max(0.001, pred)


def _ewma_vol(vols, alpha=0.1):
    """Naive EWMA volatility"""
    if not vols:
        return 0.02
    pred = vols[-1]
    for v in reversed(vols[:-1]):
        pred = alpha * v + (1 - alpha) * pred
    return pred


def _garch_like(vols, omega=0.00001, alpha=0.1, beta=0.85):
    """GARCH(1,1)-style: σ² = ω + α·r² + β·σ²"""
    if len(vols) < 2:
        return vols[-1] if vols else 0.02
    sigma_sq = vols[-1] ** 2
    r_sq = ((vols[-1] - vols[-2]) / 252) ** 2 if len(vols) > 1 else 0.0001
    sigma_sq = omega + alpha * r_sq + beta * sigma_sq
    return math.sqrt(max(0.0001, sigma_sq))


def _stoch_vol_levy(prices):
    """Stoch Vol Lévy proxy — EWMA on returns"""
    if len(prices) < 3:
        return 0.02
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] > 0 and prices[i] > 0:
            returns.append(math.log(prices[i] / prices[i-1]))
    if len(returns) < 2:
        return 0.02
    lam = 0.94
    vol_sq = returns[0] ** 2
    for t in range(1, len(returns)):
        vol_sq = lam * vol_sq + (1 - lam) * (returns[t] ** 2)
    return math.sqrt(vol_sq) * math.sqrt(252)


def main():
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'bitcoin_daily_2015_2025.json')
    with open(data_path) as f:
        data = json.load(f)
    prices = data['prices']
    dates = data.get('dates', [])

    vols = _rolling_volatility(prices, window=20)
    window = 60

    results = {
        'uvrk1': [],
        'garch': [],
        'stoch_vol_levy': [],
        'naive_ewma': [],
    }

    for i in range(window, len(vols) - 1):
        v_actual = vols[i + 1]
        vol_history = vols[:i+1]
        price_slice = prices[:20+i+1]

        uvrk_pred = _uvrk_predict(vols, i, window, prices=price_slice)
        pred = _stoch_vol_levy(price_slice) if len(price_slice) > 30 else 0.02
        garch_pred = _garch_like(vol_history)
        ewma_pred = _ewma_vol(vol_history)

        results['uvrk1'].append(abs(uvrk_pred - v_actual))
        results['stoch_vol_levy'].append(abs(pred - v_actual))
        results['garch'].append(abs(garch_pred - v_actual))
        results['naive_ewma'].append(abs(ewma_pred - v_actual))

    n = len(results['uvrk1'])
    win_rates = {}
    win_counts = {}
    for model in results:
        if model == 'uvrk1':
            continue
        wins = sum(1 for j in range(n) if results['uvrk1'][j] < results[model][j])
        win_counts[model] = wins
        win_rates[model] = wins / n * 100

    print("🏅 OLYMPIC 10-YEAR BACKTEST")
    print("=" * 60)
    print(f"Data: {len(prices)} days ({dates[0] if dates else '?'} to {dates[-1] if dates else '?'})")
    print(f"Test days: {n}")

    print("\n📊 Win Rate (days UVRK-1 beats competitor):")
    for model, rate in win_rates.items():
        stars = '⭐' * int(rate / 10)
        print(f"  vs {model:15}: {rate:5.1f}% {stars}")

    # Statistical significance (binomial test: H0: true win rate = 50%)
    if SCIPY_AVAILABLE:
        print("\n📊 Statistical Significance (binomial test, H0: p=0.5):")
        for model in win_counts:
            wins = win_counts[model]
            # One-sided: probability of >= wins if true p=0.5
            p_value = stats.binomtest(wins, n=n, p=0.5, alternative='greater').pvalue
            sig = "✅ p<0.05" if p_value < 0.05 else "⚠️ p≥0.05"
            print(f"  vs {model:15}: p={p_value:.4f} {sig}")
    else:
        print("\n📊 (Install scipy for statistical significance)")

    print("\n📊 Average MAE Improvement:")
    uvrk_avg = sum(results['uvrk1']) / n
    for model in results:
        if model != 'uvrk1':
            avg = sum(results[model]) / n
            improvement = (avg - uvrk_avg) / uvrk_avg * 100 if uvrk_avg > 0 else 0
            print(f"  vs {model:15}: {improvement:+.1f}% better")

    # Subperiod robustness: split into 3 periods
    third = n // 3
    periods = [(0, third, "2015-2018"), (third, 2 * third, "2018-2021"), (2 * third, n, "2021-2025")]
    print("\n📊 Subperiod Win Rate vs naive_ewma:")
    for start, end, label in periods:
        sub_wins = sum(1 for j in range(start, end) if results['uvrk1'][j] < results['naive_ewma'][j])
        sub_n = end - start
        sub_rate = sub_wins / sub_n * 100 if sub_n > 0 else 0
        print(f"  {label:12}: {sub_rate:5.1f}% ({sub_wins}/{sub_n})")

    # Tail sensitivity: high-vol days (top 10% by actual vol)
    actual_vols = vols[window + 1 : window + n + 1]
    vol_threshold = sorted(actual_vols)[max(0, int(0.9 * n) - 1)] if n >= 10 else 0.5
    tail_idx = [j for j in range(n) if j < len(actual_vols) and actual_vols[j] >= vol_threshold]
    if len(tail_idx) >= 10:
        tail_wins = sum(1 for j in tail_idx if results['uvrk1'][j] < results['naive_ewma'][j])
        tail_rate = tail_wins / len(tail_idx) * 100
        print(f"\n📊 Tail (top 10% vol days): {tail_rate:.1f}% win rate ({tail_wins}/{len(tail_idx)})")

    # UVRK-1 must beat naive baseline on >50% of days
    assert win_rates.get('naive_ewma', 0) > 50, f"❌ UVRK-1 must beat naive_ewma (got {win_rates.get('naive_ewma', 0):.1f}%)"

    # If scipy available, require significance vs naive_ewma
    if SCIPY_AVAILABLE:
        p_naive = stats.binomtest(win_counts['naive_ewma'], n=n, p=0.5, alternative='greater').pvalue
        assert p_naive < 0.05, f"❌ Win rate vs naive_ewma not statistically significant (p={p_naive:.4f})"

    print("\n✅ UVRK-1 beats naive baseline on most days")


if __name__ == "__main__":
    main()
