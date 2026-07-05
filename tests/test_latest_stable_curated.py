from pathlib import Path


def test_latest_stable_curated_structure_exists():
    latest = Path("outputs/latest_stable")
    assert (latest / "README.md").exists()
    assert (latest / "archive_manifest.md").exists()
    for category in ["forward", "localization", "error_analysis"]:
        assert (latest / "figures" / category).exists()
        assert (latest / "animations" / category).exists()
        assert (latest / "reports" / category).exists()
    for old in ["core", "diagnostics", "uncertainty", "reference_only"]:
        assert not (latest / "figures" / old).exists()


def test_latest_stable_root_figures_are_not_flat_png_dump():
    latest = Path("outputs/latest_stable")
    assert len(list((latest / "figures").glob("*.png"))) == 0
    summary = (latest / "summary.md").read_text(encoding="utf-8")
    assert "Stage 5H" in summary
    assert "manual_review_figures" in summary
    assert "ready_for_2p5d" in summary


def test_latest_stable_stage5h_reports_and_no_root_dump():
    latest = Path("outputs/latest_stable")
    assert len(list((latest / "figures").glob("*.png"))) == 0
    assert len(list((latest / "animations").glob("*.gif"))) == 0
    assert len(list((latest / "reports").glob("*.md"))) == 0
    for rel in [
        "reports/error_analysis/report_latest_stable_file_audit.md",
        "reports/error_analysis/report_figure_quality_check.md",
        "reports/error_analysis/report_figure_deduplication.md",
        "reports/error_analysis/report_figure_language_check.md",
        "reports/error_analysis/report_latest_stable_tree_snapshot.md",
        "reports/error_analysis/report_manual_review_readiness.md",
        "reports/forward/report_elastic2d_rayleigh_benchmark.md",
        "reports/forward/report_velocity_model_physics_bridge.md",
    ]:
        assert (latest / rel).exists()
    summary = (latest / "summary.md").read_text(encoding="utf-8")
    assert "active_velocity_model" in summary
    assert "Stage 3" not in summary
