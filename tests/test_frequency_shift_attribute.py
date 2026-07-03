import numpy as np

from src.forward.wavelet import ricker
from src.localization.attribute_scoring import compute_frequency_shift_score, spectral_centroid


def test_spectral_centroid_detects_high_frequency_content():
    dt = 0.001
    t = np.arange(101) * dt
    low = ricker(t - 0.05, 15.0)
    high = ricker(t - 0.05, 60.0)
    assert spectral_centroid(high, dt) > spectral_centroid(low, dt)


def test_frequency_shift_score_detects_centroid_drop():
    dt = 0.001
    time_axis = np.arange(220) * dt
    candidate_times = np.full((1, 1), 0.05)
    low_local = ricker(time_axis - 0.05, 15.0)
    high_background = ricker(time_axis - 0.13, 60.0)
    shifted = (low_local + high_background).reshape(1, -1, 1)

    same_local = ricker(time_axis - 0.05, 45.0)
    same_background = ricker(time_axis - 0.13, 45.0)
    unshifted = (same_local + same_background).reshape(1, -1, 1)

    shifted_score = compute_frequency_shift_score(shifted, time_axis, candidate_times, 0.02)
    unshifted_score = compute_frequency_shift_score(unshifted, time_axis, candidate_times, 0.02)
    assert shifted_score > unshifted_score
    assert shifted_score > 0.1

