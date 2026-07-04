from main import args_to_params, parse_arguments
from src.validation.elastic_vs_kinematic import run_elastic_vs_kinematic


def test_elastic_vs_kinematic_overlay_data_can_generate():
    params = args_to_params(parse_arguments(["--elastic2d-duration-s", "0.025"]))
    result = run_elastic_vs_kinematic(params)
    assert result["residual_gather"].shape[1] == len(result["kinematic_curve_s"])
    assert 0.0 <= result["curve_energy_ratio"] <= 1.0
    assert "main_conclusion" in result
