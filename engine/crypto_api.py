"""
Crypto API stub — transaction data and benchmark
Extend with real CoinGecko/Binance when available.
"""

import hashlib
from typing import Dict, Any, Optional


def get_transactions(address: str) -> Dict[str, Any]:
    """
    Get on-chain transaction summary for address.
    Stub: derives deterministic values from address hash.
    Replace with real API (e.g. blockchain explorer) when available.
    """
    h = hashlib.sha256(address.encode()).hexdigest()
    return {
        'tx_count': int(h[:4], 16) % 1000,
        'avg_value': (int(h[4:8], 16) % 10000) / 100,
        'age_days': (int(h[8:12], 16) % 2000),
        'volatility_proxy': (int(h[12:16], 16) % 50) / 1000 + 0.02,  # 0.02–0.07
    }


def get_stoch_vol_levy(address: str) -> float:
    """
    Stoch Vol Lévy benchmark for comparison.
    Stub: returns typical benchmark. Replace with real model when available.
    """
    h = hashlib.sha256(address.encode()).hexdigest()
    # Typical benchmark ~0.15, vary slightly by address
    return 0.12 + (int(h[:4], 16) % 10) / 100
