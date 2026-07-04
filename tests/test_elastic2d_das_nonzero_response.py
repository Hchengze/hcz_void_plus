from main import args_to_params, parse_arguments
from src.validation.elastic2d_das_response import run_elastic2d_das_nonzero_check


def test_elastic2d_das_nonzero_check_reports_default_not_used_for_localization():
    params = args_to_params(
        parse_arguments(
            [
                "--elastic2d-nx",
                "41",
                "--elastic2d-nz",
                "31",
                "--elastic2d-duration-s",
                "0.015",
                "--elastic2d-snapshot-count",
                "2",
            ]
        )
    )
    result = run_elastic2d_das_nonzero_check(params)
    assert set(item["source_type"] for item in result["cases"].values()) == {
        "vertical_force",
        "horizontal_force",
    }
    assert {item["gauge_length_m"] for item in result["cases"].values()} == {0.5, 1.0, 2.0, 4.0}
    assert result["das_gauge_nonzero_status"] in {"nonzero", "zero_or_too_weak"}
    assert result["default_localization_should_use_gauge_strain"] is False
    assert result["best_velocity_gauge_case"] in result["cases"]
    assert result["best_displacement_gauge_case"] in result["cases"]
