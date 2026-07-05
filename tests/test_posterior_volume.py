import numpy as np

from src.localization.posterior_volume import build_posterior_from_score, score_to_posterior_probability


def test_posterior_probability_volume_is_normalized():
    score = np.zeros((3, 2, 2), dtype=float)
    score[1, 1, 0] = 5.0
    posterior = score_to_posterior_probability(score, temperature=0.2)
    assert posterior.shape == score.shape
    assert np.isclose(np.sum(posterior), 1.0)
    assert np.argmax(posterior) == np.argmax(score)


def test_posterior_summary_contains_peak_mean_covariance_and_axes():
    score = np.zeros((3, 3, 2), dtype=float)
    score[2, 1, 1] = 3.0
    result = build_posterior_from_score(
        score,
        np.array([0.0, 1.0, 2.0]),
        np.array([0.0, 1.0, 2.0]),
        np.array([1.0, 2.0]),
        temperature=0.3,
    )
    assert result["posterior_peak_location"]["x_m"] == 2.0
    assert np.asarray(result["posterior_covariance_3x3"]).shape == (3, 3)
    assert np.asarray(result["uncertainty_ellipsoid_axes"]).shape == (3,)
