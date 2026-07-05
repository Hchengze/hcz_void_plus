from pathlib import Path


def test_summary_manual_review_files_exist():
    latest = Path("outputs/latest_stable")
    manual_figures = [
        "figures/forward/fig_geometry_3d_overview.png",
        "figures/forward/fig_velocity_model_active_badge.png",
        "figures/forward/fig_velocity_model_physics_bridge.png",
        "figures/forward/fig_elastic2d_rayleigh_benchmark_matrix.png",
        "figures/forward/fig_elastic2d_rayleigh_velocity_error.png",
        "figures/forward/fig_elastic2d_das_best_case.png",
        "figures/localization/fig_3d_high_score_region.png",
        "figures/localization/fig_recommended_location_3d.png",
        "figures/localization/fig_3d_uncertainty_box.png",
        "figures/error_analysis/fig_stage5h_status_badge.png",
    ]
    manual_animations = [
        "animations/forward/anim_multishot_forward_overview.gif",
        "animations/forward/anim_single_shot_wavefield.gif",
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
