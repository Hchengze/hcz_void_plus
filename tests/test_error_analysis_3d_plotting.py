from src.visualization.plot_error_analysis_3d import plot_rayleigh_pick_interpretation, plot_stage5g_status_badge


def test_error_analysis_3d_plotting_functions_run(tmp_path):
    status = {
        "rayleigh_like_event_detected": False,
        "das_gauge_final_status": "nonzero_but_weak_not_for_default_localization",
        "ready_for_2p5d": False,
    }
    benchmark = {
        "best_case": "staggered_traction_variant",
        "rayleigh_like_event_detected": False,
        "best_case_metrics": {
            "surface_event_energy": 0.2,
            "body_wave_leakage_indicator": 0.5,
            "boundary_reflection_indicator": 0.4,
            "late_coda_indicator": 0.3,
        },
    }
    plot_stage5g_status_badge(status, tmp_path / "fig_stage5g_status_badge.png")
    plot_rayleigh_pick_interpretation(benchmark, tmp_path / "fig_rayleigh_pick_interpretation.png")
    assert (tmp_path / "fig_stage5g_status_badge.png").exists()
    assert (tmp_path / "fig_rayleigh_pick_interpretation.png").exists()
