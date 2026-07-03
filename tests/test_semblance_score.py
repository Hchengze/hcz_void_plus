import numpy as np

from src.forward.wavelet import ricker
from src.localization.attribute_scoring import compute_semblance_score


def test_semblance_high_for_consistent_aligned_waveforms():
    time_axis = np.arange(101) * 0.001
    candidate_times = np.full((2, 3), 0.05)
    wavelet = ricker(time_axis - 0.05, 35.0)
    data = np.tile(wavelet[None, :, None], (2, 1, 3))
    score = compute_semblance_score(data, time_axis, candidate_times, 0.02)
    assert score > 0.95


def test_semblance_lower_for_random_phase_waveforms():
    time_axis = np.arange(101) * 0.001
    candidate_times = np.full((2, 3), 0.05)
    rng = np.random.default_rng(123)
    data = rng.normal(size=(2, 101, 3))
    score = compute_semblance_score(data, time_axis, candidate_times, 0.02)
    assert 0.0 <= score < 0.7

