import numpy as np

from src.forward.wavelet import ricker
from src.localization.attribute_scoring import compute_matched_wavelet_score


def test_matched_wavelet_score_prefers_ricker_window():
    time_axis = np.arange(101) * 0.001
    candidate_times = np.full((1, 1), 0.05)
    wavelet = ricker(time_axis - 0.05, 35.0)
    data_ricker = wavelet.reshape(1, -1, 1)
    rng = np.random.default_rng(42)
    data_noise = rng.normal(scale=0.2, size=data_ricker.shape)

    score_ricker = compute_matched_wavelet_score(data_ricker, time_axis, candidate_times, 0.02, 35.0)
    score_noise = compute_matched_wavelet_score(data_noise, time_axis, candidate_times, 0.02, 35.0)

    assert score_ricker > 0.95
    assert score_ricker > score_noise


def test_matched_wavelet_score_handles_out_of_bounds_window():
    time_axis = np.arange(30) * 0.001
    data = np.ones((2, 30, 3))
    candidate_times = np.full((2, 3), 2.0)
    score = compute_matched_wavelet_score(data, time_axis, candidate_times, 0.02, 35.0)
    assert score == 0.0

