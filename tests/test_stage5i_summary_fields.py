from pathlib import Path


def test_latest_stable_summary_contains_stage5j_algorithm_fields():
    summary = Path("outputs/latest_stable/summary.md")
    assert summary.exists()
    text = summary.read_text(encoding="utf-8")
    assert "Stage 5J" in text
    for field in [
        "volume_wavefield_available",
        "volume_wavefield_grid_shape",
        "volume_wavefield_uses_depth",
        "volume_wavefield_uses_velocity_path_integration",
        "volume_wavefield_is_kinematic_proxy",
        "shot_gather_velocity_overlay_available",
        "attenuation_model_enabled",
        "direct_attenuation_applied",
        "scatter_attenuation_applied",
        "attenuation_rms_difference",
        "forward_localization_link_status",
        "scan_candidate_uses_path_integration",
        "scan_uses_representative_velocity",
        "multi_attribute_inversion_enabled",
        "posterior_volume_status",
        "posterior_peak_location",
        "posterior_mean_location",
        "posterior_uncertainty_axes",
        "geometry_resolution_status",
        "ambiguity_warning",
        "ready_for_2p5d",
    ]:
        assert field in text
