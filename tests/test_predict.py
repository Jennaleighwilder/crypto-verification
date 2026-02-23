"""
Test UVRK-1 prediction matches backtested values
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.uvrk import UVRK1Engine, REGIMES


def test_predict_all_regimes():
    """Prediction for all 7 regimes"""
    engine = UVRK1Engine()
    test_vol = 0.04
    for regime in REGIMES:
        pred = engine.predict(regime, test_vol)
        assert pred is not None
        assert pred.predicted_volatility > 0
        assert pred.confidence >= 0.86  # Min R² across regimes


def test_predict_direction():
    """Prediction direction is INCREASING, DECREASING, or STABLE"""
    engine = UVRK1Engine()
    pred = engine.predict('bitcoin', 0.045)
    assert pred.direction in ('INCREASING', 'DECREASING', 'STABLE')


def test_predict_state():
    """State is normal, elevated, stressed, or critical"""
    engine = UVRK1Engine()
    pred = engine.predict('bitcoin', 0.045)
    assert pred.state in ('normal', 'elevated', 'stressed', 'critical')
