import numpy as np

from main import args_to_params, parse_arguments
from src.forward.kinematic_volume_response import compute_kinematic_volume_response
from src.geometry.acquisition_geometry import generate_source_xyz
from src.model.anomalies import anomaly_to_scatter_points, build_anomaly_from_params
from src.model.velocity_model import build_velocity_model


def _small_params():
    return args_to_params(
        parse_arguments(
            [
                "--source-shot-count",
                "2",
                "--fiber-channel-count",
                "11",
                "--time-record-length-s",
                "0.20",
                "--volume-wavefield-nx",
                "12",
                "--volume-wavefield-ny",
                "8",
                "--volume-wavefield-nh",
                "5",
                "--volume-wavefield-frame-count",
                "3",
                "--volume-wavefield-max-scatter-points",
                "4",
                "--save-figures",
                "false",
            ]
        )
    )


def test_kinematic_volume_response_has_depth_and_path_integration():
    params = _small_params()
    source_xyz = generate_source_xyz(params)
    anomaly = build_anomaly_from_params(params)
    scatter_xyz, scatter_weight = anomaly_to_scatter_points(anomaly, params.anomaly.scatter_point_mode)
    velocity_model = build_velocity_model(params)

    result = compute_kinematic_volume_response(params, source_xyz, scatter_xyz, scatter_weight, velocity_model)
    frames = result["volume_frames"]
    meta = result["metadata"]

    assert frames.shape == (3, 5, 8, 12)
    assert result["depth_axis_m"].ndim == 1
    assert result["depth_axis_m"].size == 5
    assert np.any(np.abs(frames) > 0.0)
    assert meta["depth_axis_positive_down"] is True
    assert meta["volume_uses_velocity_path_integration"] is True
    assert meta["volume_uses_attenuation"] is True
    assert meta["volume_is_kinematic_proxy"] is True
