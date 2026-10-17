"""Competition metric: Tweedie D² with power 1.5 (matches sklearn.metrics.d2_tweedie_score)."""
import numpy as np

POWER = 1.5
PRED_FLOOR = 1e-6  # Tweedie deviance is undefined at prediction 0 for 1 < p < 2


def tweedie_deviance(y, mu, power=POWER, sample_weight=None):
    """Mean unit Tweedie deviance for 1 < power < 2."""
    y = np.asarray(y, dtype=float)
    mu = np.asarray(mu, dtype=float)
    if np.any(y < 0) or np.any(mu <= 0):
        raise ValueError("Tweedie 1<p<2 requires y >= 0 and mu > 0")
    p = power
    dev = 2 * (np.power(y, 2 - p) / ((1 - p) * (2 - p))
               - y * np.power(mu, 1 - p) / (1 - p)
               + np.power(mu, 2 - p) / (2 - p))
    return float(np.average(dev, weights=sample_weight))


def d2_tweedie(y, mu, power=POWER, sample_weight=None):
    """1 - D(y, mu) / D(y, ybar): share of deviance explained vs a constant prediction."""
    y = np.asarray(y, dtype=float)
    ybar = np.average(y, weights=sample_weight)
    num = tweedie_deviance(y, mu, power, sample_weight)
    den = tweedie_deviance(y, np.full_like(y, ybar), power, sample_weight)
    return 1.0 - num / den
