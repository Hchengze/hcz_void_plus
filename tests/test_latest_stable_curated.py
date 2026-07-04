from pathlib import Path


def test_latest_stable_curated_structure_exists():
    latest = Path("outputs/latest_stable")
    assert (latest / "README.md").exists()
    assert (latest / "archive_manifest.md").exists()
    for category in ["core", "forward", "localization", "uncertainty", "diagnostics"]:
        assert (latest / "figures" / category).exists()
        assert (latest / "reports" / category).exists()


def test_latest_stable_root_figures_are_not_flat_png_dump():
    latest = Path("outputs/latest_stable")
    root_pngs = list((latest / "figures").glob("*.png"))
    assert len(root_pngs) == 0
    assert len(list((latest / "figures" / "core").glob("*.png"))) <= 8
    summary = (latest / "summary.md").read_text(encoding="utf-8")
    assert "Stage 5D" in summary
    assert "latest_stable_curated" in summary


def test_latest_stable_stage5d_core_reports_and_no_root_png_dump():
    latest = Path("outputs/latest_stable")
    assert len(list((latest / "figures").glob("*.png"))) == 0
    assert len(list((latest / "reports").glob("*.md"))) == 0
    assert (latest / "reports" / "core" / "report_repository_health.md").exists()
    assert (latest / "reports" / "core" / "report_figure_self_check.md").exists()
    assert (latest / "reports" / "diagnostics" / "report_velocity_model_audit.md").exists()
    summary = (latest / "summary.md").read_text(encoding="utf-8")
    assert "active_velocity_model_type" in summary
    assert "Stage 3" not in summary
