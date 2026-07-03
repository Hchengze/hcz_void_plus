import numpy as np

from main import args_to_params, parse_arguments
from src.features.direct_arrival import predict_direct_arrival_times
from src.features.direct_wave_mute import mute_direct_wave
from src.features.local_energy import extract_window_energy
from src.model.velocity_model import build_velocity_model


def test_direct_times_and_mute_shape():
    params = args_to_params(
        parse_arguments(["--fiber-channel-count", "12", "--source-shot-count", "2", "--gauge-length-m", "4"])
    )
    velocity_model = build_velocity_model(params)
    direct_times = predict_direct_arrival_times(
        params, params.derived.source_xyz, params.derived.receiver_xyz, velocity_model
    )
    data = np.ones((params.source.shot_count, params.derived.nt, params.fiber.channel_count), dtype=float)
    muted = mute_direct_wave(data, params.derived.time_axis, direct_times, 0.01)

    assert direct_times.shape == (params.source.shot_count, params.fiber.channel_count)
    assert muted.shape == data.shape
    assert np.sum(muted) < np.sum(data)


def test_extract_window_energy_is_safe_for_out_of_range_times():
    data = np.ones((1, 10, 2), dtype=float)
    time_axis = np.arange(10, dtype=float) * 0.1
    target_times = np.array([[0.2, 99.0]])
    energy = extract_window_energy(data, time_axis, target_times, 0.05)

    assert energy.shape == (1, 2)
    assert energy[0, 0] > 0
    assert energy[0, 1] == 0
