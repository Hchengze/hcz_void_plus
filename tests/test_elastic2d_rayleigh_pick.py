from main import args_to_params, parse_arguments
from src.validation.elastic2d_rayleigh_validation import run_elastic2d_rayleigh_validation


def test_elastic2d_rayleigh_pick_diagnostics_include_source_and_window():
    params = args_to_params(
        parse_arguments(
            [
                "--elastic2d-duration-s",
                "0.025",
                "--elastic2d-source-type",
                "horizontal_force",
                "--elastic2d-source-depth-m",
                "0.3",
            ]
        )
    )
    result = run_elastic2d_rayleigh_validation(params)
    assert result["source_type"] == "horizontal_force"
    assert result["source_depth_m"] >= 0.0
    assert result["pick_vmin_mps"] < result["pick_vmax_mps"]
    assert len(result["pick_time_s"]) == len(result["pick_offset_m"])
    assert "rayleigh_pick_interpretation" in result
