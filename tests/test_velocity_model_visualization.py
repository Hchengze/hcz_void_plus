import numpy as np

from main import args_to_params, parse_arguments
from src.visualization.plot_velocity_model import (
    plot_uniform_vs_layered_travel_time_difference,
    plot_velocity_model_2d_slice_current,
    plot_velocity_model_active_badge,
    plot_velocity_model_profile_current,
    plot_velocity_sampling_paths_current,
)


def test_velocity_model_visualization_outputs_current_model_figures(tmp_path):
    params = args_to_params(parse_arguments([]))
    scatter_xyz = np.array([[params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m]], dtype=float)
    audit = {
        "active_velocity_model_type": "layered",
        "active_velocity_model_confirmed": True,
        "velocity_model_used_by_direct": True,
        "velocity_model_used_by_scatter": True,
        "velocity_model_used_by_scan": True,
    }
    profile = tmp_path / "fig_velocity_model_profile_current.png"
    slice_fig = tmp_path / "fig_velocity_model_2d_slice_current.png"
    paths_fig = tmp_path / "fig_velocity_sampling_paths_current.png"
    diff_fig = tmp_path / "fig_uniform_vs_layered_travel_time_difference.png"
    badge = tmp_path / "fig_velocity_model_active_badge.png"

    plot_velocity_model_profile_current(params, profile)
    plot_velocity_model_2d_slice_current(params, slice_fig)
    sampling = plot_velocity_sampling_paths_current(
        params,
        params.derived.source_xyz,
        params.derived.receiver_xyz,
        scatter_xyz,
        paths_fig,
    )
    diff = plot_uniform_vs_layered_travel_time_difference(
        params,
        params.derived.source_xyz,
        params.derived.receiver_xyz,
        diff_fig,
    )
    plot_velocity_model_active_badge(params, audit, badge)

    for path in [profile, slice_fig, paths_fig, diff_fig, badge]:
        assert path.exists()
        assert path.stat().st_size > 1024
    assert sampling["velocity_min_mps"] > 0.0
    assert diff["direct_diff_rms_ms"] > 0.0
