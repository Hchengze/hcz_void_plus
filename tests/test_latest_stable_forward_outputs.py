from pathlib import Path


def test_latest_stable_stage5f_forward_outputs_are_curated():
    latest = Path("outputs/latest_stable")
    for name in [
        "fig_elastic2d_rayleigh_benchmark_matrix.png",
        "fig_elastic2d_rayleigh_velocity_error.png",
        "fig_elastic2d_surface_event_ridge.png",
        "fig_elastic2d_free_surface_mode_comparison.png",
        "fig_elastic2d_boundary_reflection_diagnostics.png",
        "fig_elastic2d_void_scattering_residual.png",
        "fig_elastic2d_das_staggered_vs_collocated.png",
        "fig_elastic2d_das_best_case.png",
        "fig_elastic2d_das_report_consistency.png",
        "fig_elastic_vs_kinematic_energy_partition.png",
    ]:
        assert (latest / "figures" / "forward" / name).exists()

    for name in [
        "report_forward_engine_ablation.md",
        "report_elastic2d_rayleigh_benchmark.md",
        "report_elastic2d_free_surface_validation.md",
        "report_elastic2d_boundary_validation.md",
        "report_elastic2d_void_scattering.md",
        "report_elastic2d_das_response.md",
    ]:
        assert (latest / "reports" / "forward" / name).exists()


def test_latest_stable_stage5f_diagnostics_outputs_are_curated():
    latest = Path("outputs/latest_stable")
    for name in [
        "fig_latest_stable_quality_summary.png",
        "fig_model_mismatch_error_summary.png",
        "fig_depth_prior_sensitivity.png",
        "fig_velocity_model_profile_current.png",
        "fig_velocity_model_active_badge.png",
        "fig_rayleigh_equivalent_vs_elastic_velocity.png",
        "fig_bridge_derived_elastic_parameters.png",
        "fig_velocity_model_physics_bridge.png",
    ]:
        assert (latest / "figures" / "diagnostics" / name).exists()

    for name in [
        "report_model_mismatch.md",
        "report_velocity_model_audit.md",
        "report_velocity_model_visualization.md",
        "report_velocity_model_physics_bridge.md",
    ]:
        assert (latest / "reports" / "diagnostics" / name).exists()
