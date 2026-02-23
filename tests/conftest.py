"""
Pytest configuration and fixtures
"""
import os
import sys

# Add project root to path
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _root)

# Synthetic Bitcoin-like data for tests (replace with real data when available)
# Format: daily closing prices, ~10 years
import json
import math
import random

def _generate_synthetic_prices(n_days=2520, seed=42):
    """Generate realistic-looking price series for testing"""
    random.seed(seed)
    price = 400  # Start ~2015 BTC
    prices = [price]
    for _ in range(n_days - 1):
        ret = random.gauss(0.0005, 0.02)
        price *= math.exp(ret)
        prices.append(max(1, price))
    return prices

SYNTHETIC_PRICES = _generate_synthetic_prices()

def _rolling_volatility(prices, window=20):
    """Annualized rolling volatility"""
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

SYNTHETIC_VOLATILITIES = _rolling_volatility(SYNTHETIC_PRICES)

# Write synthetic data for tests that expect a file
DATA_DIR = os.path.join(_root, 'tests', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

_bitcoin_data_path = os.path.join(DATA_DIR, 'bitcoin_daily_2015_2025.json')
if not os.path.exists(_bitcoin_data_path):
    with open(_bitcoin_data_path, 'w') as f:
        json.dump({
            'prices': SYNTHETIC_PRICES,
            'volatilities': SYNTHETIC_VOLATILITIES,
            'source': 'synthetic',
            'note': 'Replace with real data: tests/data/bitcoin_daily_2015_2025.json'
        }, f, indent=2)
