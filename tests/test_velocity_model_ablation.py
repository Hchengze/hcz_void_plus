from main import args_to_params, parse_arguments
from src.model.anomalies import anomaly_to_scatter_points, build_anomaly_from_params
from src.validation.velocity_model_ablation import run_velocity_model_ablation


def test_velocity_model_ablation_runs():
    params = args_to_params(
        parse_arguments(
            [
                "--fiber-channel-count",
                "24",
                "--source-shot-count",
                "4",
                "--gauge-length-m",
                "4",
                "--scan-x-min-m",
                "56",
                "--scan-x-max-m",
                "64",
                "--scan-x-step-m",
                "4",
                "--scan-y-min-m",
                "6",
                "--scan-y-max-m",
                "12",
                "--scan-y-step-m",
                "3",
                "--scan-depth-min-m",
                "1",
                "--scan-depth-max-m",
                "5",
                "--scan-depth-step-m",
                "2",
            ]
        )
    )
    anomaly = build_anomaly_from_params(params)
    scatter_xyz, scatter_weight = anomaly_to_scatter_points(anomaly, params.anomaly.scatter_point_mode)
    result = run_velocity_model_ablation(params, params.derived.source_xyz, params.derived.receiver_xyz, scatter_xyz, scatter_weight)
    assert "layered" in result["cases"]
    assert "uniform" in result["cases"]
    assert "best_truth_error_case" in result
