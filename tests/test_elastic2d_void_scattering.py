import numpy as np

from main import args_to_params, parse_arguments
from src.validation.elastic2d_void_scattering import run_elastic2d_void_scattering


def test_elastic2d_void_scattering_residual_is_nonzero():
    params = args_to_params(parse_arguments(["--elastic2d-duration-s", "0.025"]))
    result = run_elastic2d_void_scattering(params)
    assert result["residual_gather"].shape == result["background_result"].surface_vz_gather.shape
    assert result["anomaly_result"].surface_vz_gather.shape == result["background_result"].surface_vz_gather.shape
    assert np.any(result["residual_gather"] != 0.0)
    assert result["void_residual_visible"] is True
