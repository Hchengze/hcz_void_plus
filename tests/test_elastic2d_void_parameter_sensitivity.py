from main import args_to_params, parse_arguments
from src.validation.elastic2d_void_scattering import run_elastic2d_void_parameter_sensitivity


def test_elastic2d_void_parameter_sensitivity_runs_small_grid():
    params = args_to_params(parse_arguments(["--elastic2d-duration-s", "0.02"]))
    result = run_elastic2d_void_parameter_sensitivity(params)
    assert result["parameter_count"] == 18
    assert result["best_case"] in result["cases"]
    assert result["best_residual_energy"] >= 0.0
    assert result["cases"][result["best_case"]]["source_type"] in {"vertical_force", "horizontal_force"}
