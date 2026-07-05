from pathlib import Path


def test_summary_manual_review_files_exist():
    latest = Path("outputs/latest_stable")
    manual_figures = [
        "figures/forward/fig_geometry_3d_overview.png",
        "figures/forward/fig_velocity_model_active_badge.png",
        "figures/forward/fig_velocity_sampling_paths_3d.png",
        "figures/forward/fig_volume_wavefield_xyz_slices.png",
        "figures/forward/fig_volume_wavefield_3d_energy_proxy.png",
        "figures/forward/fig_shot_gather_with_velocity_model.png",
        "figures/forward/fig_shot_gather_attenuation_comparison.png",
        "figures/localization/fig_3d_posterior_volume.png",
        "figures/localization/fig_3d_uncertainty_ellipsoid.png",
        "figures/error_analysis/fig_forward_localization_consistency.png",
    ]
    manual_animations = [
        "animations/forward/anim_single_shot_volume_wavefield.gif",
        "animations/forward/anim_multishot_forward_overview.gif",
    ]
    summary = (latest / "summary.md").read_text(encoding="utf-8")
    assert "algorithm_commit" in summary
    assert "latest_stable_commit" in summary
    assert "commit id" not in summary.lower()
    for rel in manual_figures + manual_animations:
        assert rel in summary
        assert (latest / rel).exists(), rel


def test_ready_for_2p5d_follows_rayleigh_status():
    text = Path("outputs/latest_stable/summary.md").read_text(encoding="utf-8")
    if "rayleigh_like_event_detected：`False`" in text or "rayleigh_like_event_detected：`False`" in text:
        assert "ready_for_2p5d = `False`" in text or "ready_for_2p5d：`False`" in text
