from main import args_to_params, parse_arguments
from src.validation.elastic_vs_kinematic import run_elastic_vs_kinematic


def test_elastic_vs_kinematic_metrics_are_bounded():
    params = args_to_params(parse_arguments(["--elastic2d-duration-s", "0.02"]))
    result = run_elastic_vs_kinematic(params)
    for key in [
        "residual_energy_near_kinematic_curve_ratio",
        "residual_energy_off_curve_ratio",
        "kinematic_curve_explained_fraction",
        "elastic_extra_event_fraction",
    ]:
        assert 0.0 <= result[key] <= 1.0
    assert isinstance(result["best_time_shift_ms"], float)
    assert "main_conclusion" in result
