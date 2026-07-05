from pathlib import Path

from src.validation.manual_review_readiness import run_manual_review_readiness


def test_manual_review_readiness_passes_current_latest_stable():
    latest = Path("outputs/latest_stable")
    result = run_manual_review_readiness(latest)

    assert result["stage"] == "Stage 5I"
    assert result["status"] == "pass"
    assert 8 <= result["manual_review_figure_count"] <= 10
    assert 2 <= result["manual_review_animation_count"] <= 4
    assert result["required_3d_figures_present"] is True
    assert result["required_animations_present"] is True
    assert "figures/forward/fig_geometry_3d_overview.png" in result["manual_review_figures"]
    assert "figures/localization/fig_3d_high_score_region.png" in result["manual_review_figures"]
    assert "animations/forward/anim_multishot_forward_overview.gif" in result["manual_review_animations"]


def test_manual_review_readiness_report_exists():
    report = Path("outputs/latest_stable/reports/error_analysis/report_manual_review_readiness.md")
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "人工建议查看顺序" in text
    assert "三维几何与定位表达" in text
