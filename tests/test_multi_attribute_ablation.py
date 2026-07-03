import numpy as np

from main import args_to_params, parse_arguments
from src.validation.multi_attribute_ablation import run_multi_attribute_ablation


def test_multi_attribute_ablation_outputs_each_group_best():
    params = args_to_params(
        parse_arguments(
            [
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
    shape = params.derived.scan_shape
    base = np.zeros(shape)
    base[1, 1, 1] = 1.0
    scan_result = {
        "attribute_score_volumes": {
            "energy_score": base,
            "normalized_energy_score": base * 0.8,
            "matched_wavelet_score": base * 0.9,
            "semblance_score": base * 0.7,
            "frequency_shift_score": np.zeros(shape),
        }
    }
    result = run_multi_attribute_ablation(params, scan_result)
    assert "energy_only" in result["groups"]
    assert "full_multi_attribute" in result["groups"]
    assert result["groups"]["full_multi_attribute"]["best_location"]["x_m"] == 60.0

