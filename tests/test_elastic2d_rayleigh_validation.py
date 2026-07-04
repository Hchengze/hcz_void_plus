from main import args_to_params, parse_arguments
from src.validation.elastic2d_rayleigh_validation import run_elastic2d_rayleigh_validation


def test_elastic2d_rayleigh_validation_returns_velocity_check():
    params = args_to_params(parse_arguments(["--elastic2d-duration-s", "0.025"]))
    result = run_elastic2d_rayleigh_validation(params)
    assert result["cfl_info"]["stable"] is True
    assert result["estimated_surface_velocity_mps"] > 0.0
    assert len(result["expected_rayleigh_like_range_mps"]) == 2
    assert "rayleigh_like_event_detected" in result
