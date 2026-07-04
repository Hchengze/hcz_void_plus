from pathlib import Path


def test_das_report_and_summary_keep_stage5g_conservative_boundary():
    latest = Path("outputs/latest_stable")
    summary = (latest / "summary.md").read_text(encoding="utf-8")
    report = (latest / "reports" / "forward" / "report_elastic2d_das_response.md").read_text(encoding="utf-8")

    assert "das_gauge_final_status" in summary
    assert "nonzero_but_weak_not_for_default_localization" in summary
    assert "default" in report.lower() or "默认" in report
    assert "not_for_default_localization" in report or "不能默认" in report or "禁止默认" in report
    assert "真实 DAS" in report or "DAS-like" in report


def test_das_stage5g_figures_exist():
    latest = Path("outputs/latest_stable")
    assert (latest / "figures" / "forward" / "fig_elastic2d_das_best_case.png").exists()
    assert (latest / "figures" / "error_analysis" / "fig_elastic2d_das_report_consistency.png").exists()
