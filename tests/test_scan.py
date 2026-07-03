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
    assert result["score_volume_active"].shape == params.derived.scan_shape
    assert result["score_volume_unweighted"].shape == params.derived.scan_shape
    assert result["score_volume_raw"].shape == params.derived.scan_shape
    assert result["score_volume_depth_weighted"].shape == params.derived.scan_shape
    assert result["raw_best_location"]
    assert result["unweighted_best_location"]
    assert result["active_best_location"]
    assert result["weighted_best_location"]
    assert result["raw_weighted_difference"]["distance_m"] >= 0.0
    assert result["score_volume_kind"] in {"raw", "depth_weighted"}
    assert np.isfinite(result["score_volume"]).all()
    assert np.all(result["score_volume_depth_weighted"] <= result["score_volume_raw"] + 1.0e-12)
    assert result["truth_error"]["distance_m"] <= 4.0


def test_normalized_energy_stack_score_volume_shape():
    params = args_to_params(
        parse_arguments(
            [
                "--score-method",
                "normalized_energy_stack",
                "--fiber-channel-count",
                "12",
                "--source-shot-count",
                "2",
                "--time-record-length-s",
                "0.2",
                "--gauge-length-m",
                "4",
                "--scan-x-min-m",
                "56",
                "--scan-x-max-m",
                "60",
                "--scan-x-step-m",
                "2",
                "--scan-y-min-m",
                "8",
                "--scan-y-max-m",
                "10",
                "--scan-y-step-m",
                "1",
                "--scan-depth-min-m",
                "1",
                "--scan-depth-max-m",
                "3",
                "--scan-depth-step-m",
                "1",
            ]
        )
    )
    data = np.ones((params.source.shot_count, params.derived.nt, params.fiber.channel_count), dtype=float)
    result = run_multishot_scan(
        data,
        params.derived.time_axis,
        params.derived.source_xyz,
        params.derived.receiver_xyz,
        build_velocity_model(params),
        build_scan_grid(params),
        params,
    )

    assert result["score_volume_raw"].shape == params.derived.scan_shape
    assert result["score_volume_depth_weighted"].shape == params.derived.scan_shape
    assert np.isfinite(result["score_volume_raw"]).all()
