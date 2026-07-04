import json
from pathlib import Path

from src.validation.scientific_figure_self_check import (
    RECOMMENDED_STAGE5E_FIGURES,
    run_scientific_figure_self_check,
    write_scientific_figure_self_check_report,
)


def test_readme_and_current_status_are_stage5e():
    readme = Path("README.md").read_text(encoding="utf-8")
    status = Path("docs/current_status.md").read_text(encoding="utf-8")
    assert "Stage 5E" in readme
    assert "Stage 5E" in status
    assert "active velocity model" in readme or "active_velocity_model" in readme
    assert "不建议进入 2.5D" in readme
    assert "Rayleigh-like 检测未通过" in status


def _make_latest(tmp_path: Path) -> Path:
    latest = tmp_path / "latest_stable"
    (latest / "metadata").mkdir(parents=True)
    for rel in RECOMMENDED_STAGE5E_FIGURES:
        path = latest / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"placeholder")
    (latest / "reports" / "diagnostics").mkdir(parents=True)
    (latest / "reports" / "forward").mkdir(parents=True)
    (latest / "summary.md").write_text(
        "# summary\n\n- stage：`Stage 5E`\n- active_velocity_model_type：`layered`\n",
        encoding="utf-8",
    )
    (latest / "reports" / "diagnostics" / "report_velocity_model_audit.md").write_text(
        "- active velocity_model_type：`layered`\n",
        encoding="utf-8",
    )
    (latest / "reports" / "forward" / "report_elastic2d_rayleigh_validation.md").write_text(
        "Rayleigh-like 检测未通过，不能宣称 Rayleigh 正演成功。\n",
        encoding="utf-8",
    )
    manifest = {
        "passed_items": [
            {
                "filename": Path(rel).name,
                "metadata": {
                    "stage": "Stage 5E",
                    "forward_engine": "layered_kinematic",
                    "velocity_model_type": "layered",
                    "required_report": "reports/forward/report_elastic2d_rayleigh_validation.md",
                },
            }
            for rel in RECOMMENDED_STAGE5E_FIGURES
        ]
    }
    (latest / "metadata" / "figure_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False),
        encoding="utf-8",
    )
    return latest


def test_scientific_figure_self_check_passes_consistent_stage5e_latest(tmp_path):
    latest = _make_latest(tmp_path)
    result = run_scientific_figure_self_check(
        latest,
        {
            "rayleigh_like_event_detected": False,
            "das_gauge_nonzero_status": "zero_or_too_weak",
            "active_velocity_model_type": "layered",
        },
    )
    assert result["status"] == "pass"
    assert result["checked_figure_count"] == len(RECOMMENDED_STAGE5E_FIGURES)
    assert 8 <= len(result["recommended_figures"]) <= 12

    report = tmp_path / "report_scientific_figure_self_check.md"
    write_scientific_figure_self_check_report(report, result)
    assert "scientific figure self-check" in report.read_text(encoding="utf-8")


def test_scientific_figure_self_check_blocks_false_rayleigh_success(tmp_path):
    latest = _make_latest(tmp_path)
    (latest / "reports" / "forward" / "report_elastic2d_rayleigh_validation.md").write_text(
        "Rayleigh-like 检测成功。\n",
        encoding="utf-8",
    )
    result = run_scientific_figure_self_check(
        latest,
        {
            "rayleigh_like_event_detected": False,
            "das_gauge_nonzero_status": "zero_or_too_weak",
            "active_velocity_model_type": "layered",
        },
    )
    assert result["status"] == "fail"
    assert result["failure_count"] >= 1
