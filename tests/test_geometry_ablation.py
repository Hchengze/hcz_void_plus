import numpy as np

from main import args_to_params, parse_arguments
from src.model.velocity_model import build_velocity_model
from src.validation.geometry_ablation import run_geometry_ablation


def test_geometry_ablation_outputs_each_case_spans():
    params = args_to_params(
        parse_arguments(
            [
                "--fiber-channel-count",
                "6",
                "--source-shot-count",
                "3",
                "--time-record-length-s",
                "0.18",
                "--gauge-length-m",
                "4",
                "--scan-x-min-m",
                "58",
                "--scan-x-max-m",
                "62",
                "--scan-x-step-m",
                "2",
                "--scan-y-min-m",
                "8",
                "--scan-y-max-m",
                "10",
                "--scan-y-step-m",
                "1",
                "--scan-depth-min-m",
                "2",
                "--scan-depth-max-m",
                "4",
                "--scan-depth-step-m",
                "1",
            ]
        )
    )
    velocity_model = build_velocity_model(params)
    scatter_xyz = np.array([[params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m]], dtype=float)
    scatter_weight = np.array([params.anomaly.scatter_strength], dtype=float)
    result = run_geometry_ablation(
        params,
        params.derived.source_xyz,
        params.derived.receiver_xyz,
        scatter_xyz,
        scatter_weight,
        velocity_model,
    )
    assert len(result["cases"]) == 4
    for item in result["cases"].values():
        assert "y_span_m" in item
        assert "depth_span_m" in item
        assert "high_score_component_count" in item

