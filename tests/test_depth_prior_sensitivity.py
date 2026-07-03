import numpy as np

from main import args_to_params, parse_arguments
from src.localization.depth_prior_sensitivity import run_depth_prior_sensitivity


def test_depth_prior_sensitivity_outputs_factors():
    params = args_to_params(parse_arguments(["--scan-x-min-m", "0", "--scan-x-max-m", "2", "--scan-y-min-m", "0", "--scan-y-max-m", "2"]))
    volume = np.ones(params.derived.scan_shape, dtype=float)
    result = run_depth_prior_sensitivity(volume, params)
    assert "off" in result["factors"]
    assert "1.0" in result["factors"]

