import numpy as np

from main import args_to_params, parse_arguments
from src.preprocessing.fk_filter import fk_velocity_filter
from src.validation.fk_filter_validation import compute_fk_amplitude_spectrum, run_fk_filter_validation


def test_fk_filter_shape_is_preserved():
    data = np.random.default_rng(0).normal(size=(2, 128, 12))
    filtered = fk_velocity_filter(data, 0.001, 1.0, 80.0, 500.0)
    assert filtered.shape == data.shape


def test_fk_validation_runs_for_straight_receiver():
    params = args_to_params(
        parse_arguments(["--fiber-channel-count", "8", "--source-shot-count", "2", "--time-record-length-s", "0.12", "--gauge-length-m", "4"])
    )
    data = np.random.default_rng(1).normal(size=(2, params.derived.nt, 8))
    direct_times = np.full((2, 8), 0.04)
    diffraction_times = np.full((2, 8), 0.07)
    result = run_fk_filter_validation(params, data, direct_times, diffraction_times)
    assert result["shape_preserved"] is True
    assert result["applicable_as_strict_fk"] is True
    freq, wavnum, amp = compute_fk_amplitude_spectrum(data[0], params.time.dt_s, params.fiber.channel_spacing_m)
    assert amp.shape == (len(freq), len(wavnum))


def test_fk_validation_warns_for_non_straight_receiver():
    params = args_to_params(
        parse_arguments(["--fiber-channel-count", "8", "--source-shot-count", "2", "--time-record-length-s", "0.12", "--gauge-length-m", "4"])
    )
    params.fiber.geometry_mode = "polyline_csv"
    data = np.random.default_rng(2).normal(size=(2, params.derived.nt, 8))
    direct_times = np.full((2, 8), 0.04)
    diffraction_times = np.full((2, 8), 0.07)
    result = run_fk_filter_validation(params, data, direct_times, diffraction_times)
    assert result["warning"]
    assert result["applicable_as_strict_fk"] is False

