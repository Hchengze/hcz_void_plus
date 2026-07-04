from pathlib import Path


def test_latest_stable_forward_outputs_are_in_forward_subfolders():
    latest = Path("outputs/latest_stable")
    for name in [
        "fig_forward_engine_comparison.png",
        "fig_acoustic2d_wavefield_snapshots.png",
        "fig_elastic2d_rayleigh_wavefield_snapshots.png",
        "fig_elastic2d_rayleigh_pick_diagnostics.png",
        "fig_elastic2d_void_scattering_residual.png",
        "fig_elastic2d_void_parameter_sensitivity.png",
        "fig_elastic2d_das_component_comparison.png",
        "fig_elastic_vs_kinematic_overlay.png",
        "fig_elastic_vs_kinematic_energy_partition.png",
        "fig_elastic2d_numerical_sensitivity_summary.png",
        "fig_elastic2d_rayleigh_pick_case_comparison.png",
        "fig_elastic2d_das_response_nonzero_check.png",
        "fig_elastic2d_das_force_direction_comparison.png",
    ]:
        assert (latest / "figures" / "forward" / name).exists()
    for name in [
        "report_forward_engine_ablation.md",
        "report_acoustic2d_prototype.md",
        "report_elastic2d_rayleigh_validation.md",
        "report_elastic2d_void_scattering.md",
        "report_elastic2d_das_response.md",
        "report_elastic_vs_kinematic.md",
        "report_elastic2d_numerical_sensitivity.md",
    ]:
        assert (latest / "reports" / "forward" / name).exists()


def test_latest_stable_velocity_model_outputs_are_in_diagnostics_subfolders():
    latest = Path("outputs/latest_stable")
    for name in [
        "fig_velocity_model_profile_current.png",
        "fig_velocity_model_2d_slice_current.png",
        "fig_velocity_sampling_paths_current.png",
        "fig_uniform_vs_layered_travel_time_difference.png",
        "fig_velocity_model_active_badge.png",
        "fig_rayleigh_equivalent_vs_elastic_velocity.png",
        "fig_elastic_vp_vs_rho_model.png",
        "fig_velocity_model_physics_bridge.png",
    ]:
        assert (latest / "figures" / "diagnostics" / name).exists()
    for name in [
        "report_velocity_model_audit.md",
        "report_velocity_model_visualization.md",
        "report_velocity_model_physics_bridge.md",
    ]:
        assert (latest / "reports" / "diagnostics" / name).exists()
