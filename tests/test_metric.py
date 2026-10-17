import numpy as np
import pytest
from sklearn.metrics import d2_tweedie_score

from src.metric import d2_tweedie, tweedie_deviance


@pytest.fixture
def sample():
    rng = np.random.default_rng(0)
    n = 5000
    mu = rng.gamma(2.0, 200.0, n)
    claims = rng.poisson(0.1, n)
    y = np.where(claims > 0, rng.gamma(2.0, mu * 5), 0.0)  # many zeros, heavy tail
    return y, mu


def test_matches_sklearn(sample):
    y, mu = sample
    assert d2_tweedie(y, mu) == pytest.approx(d2_tweedie_score(y, mu, power=1.5), rel=1e-10)


def test_constant_mean_scores_zero(sample):
    y, _ = sample
    assert d2_tweedie(y, np.full_like(y, y.mean())) == pytest.approx(0.0, abs=1e-12)


def test_zero_prediction_rejected(sample):
    y, mu = sample
    mu = mu.copy(); mu[0] = 0.0
    with pytest.raises(ValueError):
        tweedie_deviance(y, mu)


def test_level_miscalibration_penalised(sample):
    """Scaling a prediction away from the right level lowers D² — level matters, not just ranking."""
    y, _ = sample
    base = np.full_like(y, y.mean())
    assert d2_tweedie(y, base * 1.3) < 0 and d2_tweedie(y, base * 0.7) < 0
