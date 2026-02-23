#!/usr/bin/env python3
"""
Fetch real Bitcoin daily prices from Yahoo Finance
"""
import json
import os
from datetime import datetime

def fetch_bitcoin_data():
    """Fetch real Bitcoin daily prices from Yahoo Finance"""
    try:
        import yfinance as yf
    except ImportError:
        print("Installing yfinance...")
        import subprocess
        subprocess.check_call(["pip", "install", "yfinance"])
        import yfinance as yf

    btc = yf.Ticker("BTC-USD")
    end_date = datetime.now()
    start_date = datetime(2015, 1, 1)

    data = btc.history(start=start_date, end=end_date)

    if data.empty or len(data) < 100:
        raise ValueError("Insufficient data from Yahoo Finance")

    prices = {
        'dates': [d.strftime('%Y-%m-%d') for d in data.index],
        'prices': data['Close'].tolist(),
        'source': 'yfinance',
        'note': 'BTC-USD daily close 2015-present'
    }

    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    out_path = os.path.join(data_dir, 'bitcoin_daily_2015_2025.json')

    with open(out_path, 'w') as f:
        json.dump(prices, f, indent=2)

    print(f"✅ Fetched {len(prices['prices'])} days of Bitcoin data")
    print(f"   From: {prices['dates'][0]} to {prices['dates'][-1]}")
    return prices


if __name__ == "__main__":
    fetch_bitcoin_data()
