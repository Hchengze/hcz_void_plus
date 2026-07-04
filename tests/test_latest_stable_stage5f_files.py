from pathlib import Path


def test_latest_stable_stage5f_file_counts_are_curated():
    latest = Path("outputs/latest_stable")
    assert latest.exists()
    assert len(list((latest / "figures").glob("*.png"))) == 0
    total_figures = len(list((latest / "figures").glob("*/*.png")))
    total_reports = len(list((latest / "reports").glob("*/*.md")))
    assert 25 <= total_figures <= 35
    assert 12 <= total_reports <= 18
    assert len(list((latest / "figures" / "core").glob("*.png"))) <= 6
    assert len(list((latest / "figures" / "forward").glob("*.png"))) <= 10
    assert len(list((latest / "figures" / "diagnostics").glob("*.png"))) <= 8


def test_latest_stable_stage5f_required_files_exist():
    latest = Path("outputs/latest_stable")
    required = [
        "figures/core/fig_stage5f_status_badge.png",
        "figures/forward/fig_elastic2d_rayleigh_benchmark_matrix.png",
        "figures/forward/fig_elastic2d_rayleigh_velocity_error.png",
        "figures/forward/fig_elastic2d_surface_event_ridge.png",
        "figures/forward/fig_elastic2d_free_surface_mode_comparison.png",
        "figures/forward/fig_elastic2d_boundary_reflection_diagnostics.png",
        "figures/forward/fig_elastic2d_das_staggered_vs_collocated.png",
        "figures/forward/fig_elastic2d_das_best_case.png",
        "figures/forward/fig_elastic2d_das_report_consistency.png",
        "figures/diagnostics/fig_bridge_derived_elastic_parameters.png",
        "figures/diagnostics/fig_latest_stable_quality_summary.png",
        "reports/core/report_latest_stable_file_audit.md",
        "reports/core/report_figure_quality_check.md",
        "reports/core/report_figure_deduplication.md",
        "reports/core/report_figure_language_check.md",
        "reports/core/report_scientific_figure_self_check.md",
        "reports/forward/report_elastic2d_rayleigh_benchmark.md",
        "reports/forward/report_elastic2d_free_surface_validation.md",
        "reports/forward/report_elastic2d_boundary_validation.md",
        "reports/forward/report_elastic2d_das_response.md",
        "reports/diagnostics/report_velocity_model_physics_bridge.md",
    ]
    for rel in required:
        assert (latest / rel).exists(), rel
