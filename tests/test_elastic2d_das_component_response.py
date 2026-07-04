from main import args_to_params, parse_arguments
from src.validation.elastic2d_das_response import run_elastic2d_das_component_response


def test_elastic2d_das_component_response_compares_sources_and_gauge_lengths():
    params = args_to_params(parse_arguments(["--elastic2d-duration-s", "0.02"]))
    result = run_elastic2d_das_component_response(params)
    assert set(result["source_cases"]) == {"vertical_force", "horizontal_force"}
    assert set(result["gauge_length_cases"]) == {"0.5", "1.0", "2.0", "4.0"}
    assert result["best_source_type_for_gauge"] in result["source_cases"]
    assert result["best_gauge_length_m"] in {0.5, 1.0, 2.0, 4.0}
    assert result["strain_shape"] == result["point_shape"]
    assert result["gauge_void_residual_rms"] >= 0.0
