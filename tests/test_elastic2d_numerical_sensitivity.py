from main import args_to_params, parse_arguments
from src.forward.elastic2d.staggered_plan import (
    build_staggered_layout,
    check_staggered_cfl,
    describe_staggered_update_placeholders,
)
from src.validation.elastic2d_numerical_sensitivity import (
    run_elastic2d_numerical_sensitivity,
    write_elastic2d_numerical_sensitivity_report,
)


def test_elastic2d_numerical_sensitivity_outputs_multiple_cases(tmp_path):
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
    result = run_elastic2d_numerical_sensitivity(params)
    assert result["case_count"] >= 5
    assert result["best_case"] in result["cases"]
    assert "likely_failure_cause" in result
    assert isinstance(result["elastic2d_ready_for_2p5d"], bool)
    for item in result["cases"].values():
        assert item["cfl_stable"] is True
        assert item["max_amplitude"] >= 0.0

    report = tmp_path / "report_elastic2d_numerical_sensitivity.md"
    write_elastic2d_numerical_sensitivity_report(report, result)
    text = report.read_text(encoding="utf-8")
    assert "elastic2d 数值敏感性" in text
    assert "未通过前不建议进入 2.5D" in text


def test_staggered_grid_plan_is_layout_and_cfl_only():
    layout = build_staggered_layout(nx=40, nz=30, dx_m=0.1, dz_m=0.1)
    assert layout.vx_shape == (30, 41)
    assert layout.vz_shape == (31, 40)
    cfl = check_staggered_cfl(vp_mps=500.0, dt_s=1.0e-5, dx_m=0.1, dz_m=0.1)
    assert cfl["stable"] is True
    assert describe_staggered_update_placeholders()
