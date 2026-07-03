import numpy as np

from main import args_to_params, parse_arguments
from src.forward.multishot_forward import synthesize_multishot_forward
from src.localization.multishot_scan import run_multishot_scan
from src.localization.scan_grid import build_scan_grid
from src.model.anomalies import anomaly_to_scatter_points, build_anomaly_from_params
from src.model.velocity_model import build_velocity_model


def _scan_params():
    return args_to_params(
        parse_arguments(
            [
                "--fiber-channel-count",
                "41",
                "--source-shot-count",
                "3",
                "--source-x-start-m",
                "20",
                "--source-shot-spacing-m",
                "20",
                "--time-record-length-s",
                "0.45",
                "--gauge-length-m",
                "4",
                "--anomaly-x0-m",
                "40",
                "--anomaly-y0-m",
                "9",
                "--anomaly-depth-m",
                "3",
                "--scatter-point-mode",
                "center",
                "--scan-x-min-m",
                "34",
                "--scan-x-max-m",
                "46",
                "--scan-x-step-m",
                "2",
                "--scan-y-min-m",
                "7",
                "--scan-y-max-m",
                "11",
                "--scan-y-step-m",
                "1",
                "--scan-depth-min-m",
                "2",
                "--scan-depth-max-m",
                "4",
                "--scan-depth-step-m",
                "0.5",
            ]
        )
    )


def test_scan_grid_and_score_volume_shape():
    params = _scan_params()
    scan_grid = build_scan_grid(params)

    assert scan_grid["shape"] == params.derived.scan_shape
    assert scan_grid["point_count"] == params.derived.scan_grid_point_count


def test_multishot_scan_finds_simple_anomaly_near_truth():
    params = _scan_params()
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
    result = run_multishot_scan(
        forward["scatter_data"],
        params.derived.time_axis,
        params.derived.source_xyz,
        params.derived.receiver_xyz,
        velocity_model,
        build_scan_grid(params),
        params,
    )

    assert result["score_volume"].shape == params.derived.scan_shape
    assert result["score_volume_raw"].shape == params.derived.scan_shape
    assert result["score_volume_depth_weighted"].shape == params.derived.scan_shape
    assert np.isfinite(result["score_volume"]).all()
    assert np.all(result["score_volume_depth_weighted"] <= result["score_volume_raw"] + 1.0e-12)
    assert result["truth_error"]["distance_m"] <= 4.0
