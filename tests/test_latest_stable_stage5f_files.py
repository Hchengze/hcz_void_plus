from pathlib import Path


def test_latest_stable_stage5i_file_counts_are_curated():
    latest = Path("outputs/latest_stable")
    assert latest.exists()
    assert len(list((latest / "figures").glob("*.png"))) == 0
    total_figures = len(list((latest / "figures").glob("*/*.png")))
    total_animations = len(list((latest / "animations").glob("*/*.gif")))
    total_reports = len(list((latest / "reports").glob("*/*.md")))
    assert 18 <= total_figures <= 24
    assert 2 <= total_animations <= 4
    assert 8 <= total_reports <= 12
    assert 8 <= len(list((latest / "figures" / "forward").glob("*.png"))) <= 10
    assert 5 <= len(list((latest / "figures" / "localization").glob("*.png"))) <= 7
    assert 5 <= len(list((latest / "figures" / "error_analysis").glob("*.png"))) <= 7


def test_latest_stable_stage5i_required_files_exist():
    latest = Path("outputs/latest_stable")
    required = [
        "figures/forward/fig_geometry_3d_overview.png",
        "figures/forward/fig_velocity_model_active_badge.png",
        "figures/forward/fig_velocity_model_physics_bridge.png",
        "figures/forward/fig_elastic2d_rayleigh_benchmark_matrix.png",
        "figures/localization/fig_3d_high_score_region.png",
        "figures/localization/fig_recommended_location_3d.png",
        "figures/localization/fig_3d_uncertainty_box.png",
        "figures/localization/fig_3d_posterior_volume.png",
        "figures/localization/fig_3d_uncertainty_ellipsoid.png",
        "figures/error_analysis/fig_stage5i_status_badge.png",
        "figures/error_analysis/fig_scan_velocity_model_consistency.png",
        "figures/error_analysis/fig_3d_geometry_resolution_analysis.png",
        "figures/error_analysis/fig_multi_peak_ambiguity_analysis.png",
        "figures/error_analysis/fig_latest_stable_quality_summary.png",
        "animations/forward/anim_multishot_forward_overview.gif",
        "animations/forward/anim_single_shot_wavefield.gif",
        "reports/error_analysis/report_latest_stable_file_audit.md",
        "reports/error_analysis/report_figure_quality_check.md",
        "reports/error_analysis/report_figure_deduplication.md",
        "reports/error_analysis/report_figure_language_check.md",
        "reports/error_analysis/report_latest_stable_tree_snapshot.md",
        "reports/error_analysis/report_manual_review_readiness.md",
        "reports/forward/report_elastic2d_rayleigh_benchmark.md",
        "reports/forward/report_elastic2d_das_response.md",
        "reports/forward/report_velocity_model_physics_bridge.md",
    ]
    for rel in required:
        assert (latest / rel).exists(), rel
