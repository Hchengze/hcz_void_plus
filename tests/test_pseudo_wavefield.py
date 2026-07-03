import numpy as np

from main import args_to_params, parse_arguments
from src.model.anomalies import anomaly_to_scatter_points, build_anomaly_from_params
from src.visualization.plot_pseudo_wavefield import compute_kinematic_pseudo_wavefield_frame


def test_pseudo_wavefield_frame_shape():
    params = args_to_params(
        parse_arguments(
            [
                "--wavefield-grid-nx",
                "24",
                "--wavefield-grid-ny",
                "16",
                "--fiber-channel-count",
                "30",
                "--gauge-length-m",
                "4",
            ]
        )
    )
    anomaly = build_anomaly_from_params(params)
    scatter_xyz, scatter_weight = anomaly_to_scatter_points(anomaly, params.anomaly.scatter_point_mode)
    grid_x, grid_y, amplitude = compute_kinematic_pseudo_wavefield_frame(
        params,
        params.derived.source_xyz,
        scatter_xyz,
        scatter_weight,
        params.velocity.rayleigh_velocity_mps,
        0.1,
    )

    assert grid_x.shape == (16, 24)
    assert grid_y.shape == (16, 24)
    assert amplitude.shape == (16, 24)
    assert np.isfinite(amplitude).all()
