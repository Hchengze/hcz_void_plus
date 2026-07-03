import numpy as np

from main import args_to_params, parse_arguments
from src.confidence.consistency import compute_multishot_consistency
from src.confidence.coupling_warning import analyze_stage3b_scan_warnings, analyze_y_depth_coupling, assign_confidence_flag
from src.confidence.peak_analysis import analyze_peak_sharpness, compute_score_contrast
from src.model.velocity_model import build_velocity_model


def test_peak_sharpness_and_score_contrast_can_compute():
    score = np.ones((5, 4, 3), dtype=float)
    score[2, 1, 1] = 10.0
    peak = analyze_peak_sharpness(score, (2, 1, 1), neighborhood_radius=1)
    contrast = compute_score_contrast(score, peak["best_score"])

    assert peak["peak_sharpness"] > 1.0
    assert contrast["score_contrast"] > 1.0
    assert contrast["score_percentile"] == 100.0


def test_multishot_consistency_can_compute():
    params = args_to_params(
        parse_arguments(
            [
                "--fiber-channel-count",
                "4",
                "--source-shot-count",
                "2",
                "--time-record-length-s",
                "0.1",
                "--gauge-length-m",
                "3",
            ]
        )
    )
    data = np.zeros((params.source.shot_count, params.derived.nt, params.fiber.channel_count), dtype=float)
    data[:, 10:13, :] = 1.0
    result = compute_multishot_consistency(
        data,
        params.derived.time_axis,
        params.derived.source_xyz,
        params.derived.receiver_xyz,
        build_velocity_model(params),
        {"x_m": params.anomaly.x0_m, "y_m": params.anomaly.y0_m, "depth_m": params.anomaly.depth_m},
        params,
    )

    assert len(result["per_shot_scores"]) == params.source.shot_count
    assert result["coefficient_of_variation"] >= 0.0


def test_y_depth_coupling_warning_triggers_and_flag_rules():
    params = args_to_params(
        parse_arguments(
            [
                "--scan-x-min-m",
                "0",
                "--scan-x-max-m",
                "2",
                "--scan-x-step-m",
                "1",
                "--scan-y-min-m",
                "0",
                "--scan-y-max-m",
                "8",
                "--scan-y-step-m",
                "2",
                "--scan-depth-min-m",
                "1",
                "--scan-depth-max-m",
                "5",
                "--scan-depth-step-m",
                "1",
                "--coupling-warning-span-y-m",
                "4",
                "--coupling-warning-span-depth-m",
                "2",
            ]
        )
    )
    score = np.zeros(params.derived.scan_shape, dtype=float)
    score[1, :, 1:4] = 10.0
    result = analyze_y_depth_coupling(
        score,
        params.derived.scan_x_grid,
        params.derived.scan_y_grid,
        params.derived.scan_depth_grid,
        (1, 2, 2),
        params,
    )

    assert result["warning"] is True
    assert result["y_span_m"] >= params.confidence.coupling_warning_span_y_m
    assert result["depth_span_m"] >= params.confidence.coupling_warning_span_depth_m
    no_stage3b_warning = {
        "best_depth_at_boundary_warning": False,
        "raw_weighted_divergence_warning": False,
        "shallow_bias_warning": False,
        "wide_y_high_score_zone_warning": False,
        "depth_prior_bias_warning": False,
    }
    assert assign_confidence_flag(3.0, 3.0, 0.1, False, True, no_stage3b_warning, params) == "low"
    assert assign_confidence_flag(3.0, 3.0, 0.1, False, False, no_stage3b_warning, params) == "high"


def test_stage3b_warnings_for_boundary_divergence_and_wide_y():
    params = args_to_params(
        parse_arguments(
            [
                "--scan-x-min-m",
                "0",
                "--scan-x-max-m",
                "2",
                "--scan-x-step-m",
                "1",
                "--scan-y-min-m",
                "0",
                "--scan-y-max-m",
                "8",
                "--scan-y-step-m",
                "2",
                "--scan-depth-min-m",
                "0.5",
                "--scan-depth-max-m",
                "4.5",
                "--scan-depth-step-m",
                "1",
                "--coupling-warning-span-y-m",
                "4",
                "--raw-weighted-depth-diff-warning-m",
                "1",
                "--raw-weighted-location-diff-warning-m",
                "2",
            ]
        )
    )
    score = np.zeros(params.derived.scan_shape, dtype=float)
    score[1, :, 0] = 10.0
    scan_result = {
        "best_location": {"x_m": 1.0, "y_m": 4.0, "depth_m": 0.5},
        "raw_weighted_difference": {"dx_m": 0.0, "dy_m": 0.0, "ddepth_m": -2.0, "distance_m": 2.0},
        "depth_prior_bias_warning": True,
    }
    warnings = analyze_stage3b_scan_warnings(
        score,
        params.derived.scan_y_grid,
        params.derived.scan_depth_grid,
        (1, 2, 0),
        scan_result,
        params,
    )

    assert warnings["best_depth_at_boundary_warning"] is True
    assert warnings["wide_y_high_score_zone_warning"] is True
    assert warnings["raw_weighted_divergence_warning"] is True
    assert warnings["shallow_bias_warning"] is True
    assert assign_confidence_flag(3.0, 3.0, 0.1, False, False, warnings, params) == "low"
