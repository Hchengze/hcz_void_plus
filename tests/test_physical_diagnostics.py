import numpy as np

from main import args_to_params, parse_arguments
from src.forward.multishot_forward import synthesize_multishot_forward
from src.model.anomalies import anomaly_to_scatter_points, build_anomaly_from_params
from src.model.velocity_model import build_velocity_model
from src.visualization.plot_physical_diagnostics import (
    plot_diffraction_travel_time_curves,
    plot_rayleigh_depth_sensitivity,
    plot_source_anomaly_receiver_path_section,
)


def _diagnostic_params(tmp_path):
    return args_to_params(
        parse_arguments(
            [
                "--output-root-dir",
                str(tmp_path),
                "--fiber-channel-count",
                "24",
                "--source-shot-count",
                "2",
                "--time-record-length-s",
                "0.25",
                "--gauge-length-m",
                "4",
                "--wavefield-grid-nx",
                "20",
                "--wavefield-grid-ny",
                "12",
            ]
        )
    )


def test_physical_diagnostic_figures_can_be_generated(tmp_path):
    params = _diagnostic_params(tmp_path)
    velocity_model = build_velocity_model(params)
    anomaly = build_anomaly_from_params(params)
    scatter_xyz, scatter_weight = anomaly_to_scatter_points(anomaly, params.anomaly.scatter_point_mode)
    forward = synthesize_multishot_forward(
        params,
        params.derived.source_xyz,
        params.derived.receiver_xyz,
        scatter_xyz,
        scatter_weight,
        velocity_model,
    )

    path_section = tmp_path / "path_section.png"
    depth_sensitivity = tmp_path / "depth_sensitivity.png"
    curves = tmp_path / "curves.png"
    plot_source_anomaly_receiver_path_section(params, params.derived.source_xyz, params.derived.receiver_xyz, path_section)
    plot_rayleigh_depth_sensitivity(params, depth_sensitivity)
    plot_diffraction_travel_time_curves(
        params,
        forward["synthetic_data"],
        params.derived.source_xyz,
        params.derived.receiver_xyz,
        velocity_model,
        {"x_m": params.anomaly.x0_m, "y_m": params.anomaly.y0_m, "depth_m": params.anomaly.depth_m},
        curves,
    )

    assert path_section.exists()
    assert depth_sensitivity.exists()
    assert curves.exists()
