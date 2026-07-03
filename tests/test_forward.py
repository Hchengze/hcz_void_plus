import numpy as np

from main import args_to_params, parse_arguments
from src.forward.multishot_forward import synthesize_multishot_forward
from src.geometry.acquisition_geometry import generate_receiver_xyz, generate_source_xyz
from src.model.anomalies import anomaly_to_scatter_points, build_anomaly_from_params
from src.model.velocity_model import build_velocity_model


def _small_params(extra=None):
    args = [
        "--fiber-channel-count",
        "15",
        "--source-shot-count",
        "3",
        "--time-record-length-s",
        "0.25",
        "--gauge-length-m",
        "4",
        "--save-figures",
        "false",
    ]
    if extra:
        args.extend(extra)
    return args_to_params(parse_arguments(args))


def _run_forward(params):
    receiver_xyz = generate_receiver_xyz(params)
    source_xyz = generate_source_xyz(params)
    anomaly = build_anomaly_from_params(params)
    scatter_xyz, scatter_weight = anomaly_to_scatter_points(anomaly, params.anomaly.scatter_point_mode)
    velocity_model = build_velocity_model(params)
    return synthesize_multishot_forward(
        params, source_xyz, receiver_xyz, scatter_xyz, scatter_weight, velocity_model
    )["synthetic_data"]


def test_forward_output_shape_is_shot_time_channel():
    params = _small_params()
    data = _run_forward(params)

    assert data.shape == (params.source.shot_count, params.derived.nt, params.fiber.channel_count)


def test_noise_is_reproducible_with_fixed_seed():
    params_a = _small_params(["--noise-enabled", "true", "--noise-snr-db", "15", "--random-seed", "7"])
    params_b = _small_params(["--noise-enabled", "true", "--noise-snr-db", "15", "--random-seed", "7"])

    data_a = _run_forward(params_a)
    data_b = _run_forward(params_b)

    assert np.allclose(data_a, data_b)
