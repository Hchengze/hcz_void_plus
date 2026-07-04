from pathlib import Path


def test_das_report_and_summary_keep_stage5f_conservative_boundary():
    latest = Path("outputs/latest_stable")
    summary = (latest / "summary.md").read_text(encoding="utf-8")
    report = (latest / "reports" / "forward" / "report_elastic2d_das_response.md").read_text(encoding="utf-8")

    assert "das_gauge_final_status" in summary
    assert "default" in report.lower() or "默认" in report
    assert "不能默认" in report or "禁止默认" in report or "not_for_default_localization" in report
    assert "真实 DAS" in report or "DAS-like" in report


def test_das_stage5f_figures_exist():
    latest = Path("outputs/latest_stable")
    for name in [
        "fig_elastic2d_das_staggered_vs_collocated.png",
        "fig_elastic2d_das_best_case.png",
        "fig_elastic2d_das_report_consistency.png",
    ]:
        assert (latest / "figures" / "forward" / name).exists()
