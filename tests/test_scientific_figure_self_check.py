import json
from pathlib import Path

from src.validation.scientific_figure_self_check import (
    RECOMMENDED_STAGE5G_FIGURES,
    run_scientific_figure_self_check,
    write_scientific_figure_self_check_report,
)


def test_readme_and_current_status_are_stage5g():
    readme = Path("README.md").read_text(encoding="utf-8")
    status = Path("docs/current_status.md").read_text(encoding="utf-8")
    assert "Stage 5G" in readme
    assert "Stage 5G" in status
    assert "active velocity model" in readme
    assert "active forward engine" in readme
    assert "ready_for_2p5d=False" in status or "ready_for_2p5d" in readme


def _make_latest(tmp_path: Path) -> Path:
    latest = tmp_path / "latest_stable"
    (latest / "metadata").mkdir(parents=True)
    for rel in RECOMMENDED_STAGE5G_FIGURES:
        path = latest / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"placeholder")
    (latest / "reports" / "forward").mkdir(parents=True)
    (latest / "reports" / "localization").mkdir(parents=True)
    (latest / "reports" / "error_analysis").mkdir(parents=True)
    (latest / "summary.md").write_text(
        "# summary\n\n- stage = Stage 5G\n- active_velocity_model = `layered`\n",
        encoding="utf-8",
    )
    (latest / "reports" / "forward" / "report_elastic2d_rayleigh_benchmark.md").write_text(
        "Rayleigh-like 检测未通过；不得宣称 Rayleigh 正演成功。\n",
        encoding="utf-8",
    )
    (latest / "reports" / "forward" / "report_elastic2d_das_response.md").write_text(
        "DAS gauge 非零但弱，不能默认用于定位。\n",
        encoding="utf-8",
    )
    manifest = {
        "passed_items": [
            {
                "filename": Path(rel).name,
                "category": Path(rel).parts[1],
                "metadata": {
                    "stage": "Stage 5G",
                    "forward_engine": "layered_kinematic",
                    "velocity_model_type": "layered",
                    "required_report": "reports/forward/report_elastic2d_rayleigh_benchmark.md",
                },
            }
            for rel in RECOMMENDED_STAGE5G_FIGURES
        ]
    }
    (latest / "metadata" / "figure_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False),
        encoding="utf-8",
    )
    return latest


def test_scientific_figure_self_check_passes_consistent_stage5g_latest(tmp_path):
    latest = _make_latest(tmp_path)
    result = run_scientific_figure_self_check(
        latest,
        {
            "rayleigh_like_event_detected": False,
            "das_gauge_final_status": "nonzero_but_weak_not_for_default_localization",
            "active_velocity_model_type": "layered",
        },
    )
    assert result["stage"] == "Stage 5G"
    assert result["status"] == "pass"
    assert result["checked_figure_count"] == len(RECOMMENDED_STAGE5G_FIGURES)
    assert 8 <= len(result["recommended_figures"]) <= 12

    report = tmp_path / "report_scientific_figure_self_check.md"
    write_scientific_figure_self_check_report(report, result)
    assert "scientific figure self-check" in report.read_text(encoding="utf-8")


def test_scientific_figure_self_check_blocks_false_rayleigh_success(tmp_path):
    latest = _make_latest(tmp_path)
    (latest / "reports" / "forward" / "report_elastic2d_rayleigh_benchmark.md").write_text(
        "Rayleigh-like 检测成功。\n",
        encoding="utf-8",
    )
    result = run_scientific_figure_self_check(
        latest,
        {
            "rayleigh_like_event_detected": False,
            "das_gauge_final_status": "nonzero_but_weak_not_for_default_localization",
            "active_velocity_model_type": "layered",
        },
    )
    assert result["status"] == "fail"
    assert result["failure_count"] >= 1
