import numpy as np

from main import args_to_params, parse_arguments
from src.features.direct_arrival import predict_direct_arrival_times
from src.model.velocity_model import build_velocity_model
from src.validation.preprocessing_ablation import run_preprocessing_ablation


def test_preprocessing_ablation_runs_all_cases():
    params = args_to_params(
        parse_arguments(
            [
                "--fiber-channel-count",
                "6",
                "--source-shot-count",
                "2",
                "--time-record-length-s",
                "0.12",
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
    rng = np.random.default_rng(0)
    data = rng.normal(size=(params.source.shot_count, params.derived.nt, params.fiber.channel_count))
    velocity_model = build_velocity_model(params)
    direct_times = predict_direct_arrival_times(params, params.derived.source_xyz, params.derived.receiver_xyz, velocity_model)
    result = run_preprocessing_ablation(
        params,
        data,
        direct_times,
        params.derived.source_xyz,
        params.derived.receiver_xyz,
        velocity_model,
    )
    assert len(result["cases"]) == 6
    for item in result["cases"].values():
        assert "best_location" in item
        assert "diffraction_curve_energy_ratio" in item

