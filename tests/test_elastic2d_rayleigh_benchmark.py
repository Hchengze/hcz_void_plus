from pathlib import Path

from main import args_to_params, parse_arguments
from src.validation.elastic2d_rayleigh_benchmark import (
    run_elastic2d_rayleigh_benchmark,
    write_elastic2d_rayleigh_benchmark_report,
)


def test_elastic2d_rayleigh_benchmark_outputs_multiple_cases(tmp_path):
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
    result = run_elastic2d_rayleigh_benchmark(params)
    assert result["stage"] == "Stage 5F"
    assert result["case_count"] >= 6
    assert result["best_case"] in result["cases"]
    assert result["staggered_grid_status"] == "implemented_minimal_validation"
    assert result["ready_for_2p5d"] == bool(result["rayleigh_like_event_detected"])
    if not result["rayleigh_like_event_detected"]:
        assert result["ready_for_2p5d"] is False

    report = tmp_path / "report_elastic2d_rayleigh_benchmark.md"
    write_elastic2d_rayleigh_benchmark_report(report, result)
    text = report.read_text(encoding="utf-8")
    assert "Rayleigh" in text
    assert "ready_for_2p5d" in text
