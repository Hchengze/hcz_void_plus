from pathlib import Path


def test_latest_stable_stage5i_forward_outputs_are_curated():
    latest = Path("outputs/latest_stable")
    for name in [
        "fig_geometry_3d_overview.png",
        "fig_velocity_model_active_badge.png",
        "fig_velocity_model_physics_bridge.png",
        "fig_velocity_sampling_paths_3d.png",
        "fig_elastic2d_rayleigh_benchmark_matrix.png",
        "fig_elastic2d_rayleigh_velocity_error.png",
        "fig_elastic2d_surface_event_ridge.png",
        "fig_elastic2d_das_best_case.png",
        "fig_single_shot_wavefield_snapshots.png",
    ]:
        assert (latest / "figures" / "forward" / name).exists()

    for name in [
        "anim_multishot_forward_overview.gif",
        "anim_single_shot_wavefield.gif",
    ]:
        assert (latest / "animations" / "forward" / name).exists()


def test_latest_stable_stage5i_localization_and_error_outputs_are_curated():
    latest = Path("outputs/latest_stable")
    for name in [
        "fig_scan_x_y_slice.png",
        "fig_scan_x_depth_slice.png",
        "fig_3d_high_score_region.png",
        "fig_recommended_location_3d.png",
        "fig_3d_uncertainty_box.png",
        "fig_3d_posterior_volume.png",
        "fig_3d_uncertainty_ellipsoid.png",
    ]:
        assert (latest / "figures" / "localization" / name).exists()

    for name in [
        "fig_stage5i_status_badge.png",
        "fig_latest_stable_quality_summary.png",
        "fig_rayleigh_pick_interpretation.png",
        "fig_elastic2d_das_report_consistency.png",
        "fig_scan_velocity_model_consistency.png",
        "fig_3d_geometry_resolution_analysis.png",
        "fig_multi_peak_ambiguity_analysis.png",
    ]:
        assert (latest / "figures" / "error_analysis" / name).exists()
