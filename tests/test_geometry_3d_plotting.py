import numpy as np

from main import args_to_params, parse_arguments
from src.geometry.acquisition_geometry import generate_receiver_xyz, generate_source_xyz
from src.visualization.plot_geometry_3d import plot_geometry_3d_overview, plot_velocity_sampling_paths_3d


def test_geometry_3d_plotting_functions_run(tmp_path):
    params = args_to_params(parse_arguments([]))
    source_xyz = generate_source_xyz(params)
    receiver_xyz = generate_receiver_xyz(params)
    scatter_xyz = np.array([[params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m]], dtype=float)
    plot_geometry_3d_overview(
        params,
        source_xyz,
        receiver_xyz,
        scatter_xyz,
        tmp_path / "fig_geometry_3d_overview.png",
    )
    summary = plot_velocity_sampling_paths_3d(
        params,
        source_xyz,
        receiver_xyz,
        scatter_xyz[0],
        tmp_path / "fig_velocity_sampling_paths_3d.png",
    )
    assert (tmp_path / "fig_geometry_3d_overview.png").exists()
    assert (tmp_path / "fig_velocity_sampling_paths_3d.png").exists()
    assert summary["sample_count"] > 0
