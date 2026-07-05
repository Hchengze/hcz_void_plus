import numpy as np

from main import args_to_params, parse_arguments
from src.forward.observation_kernel_3d import (
    build_observation_paths_3d,
    candidate_grid_to_xyz,
    synthesize_gather_from_observation_paths,
)
from src.geometry.acquisition_geometry import generate_receiver_xyz, generate_source_xyz
from src.model.attenuation_model import build_attenuation_model
from src.model.velocity_model import build_velocity_model, compute_kinematic_travel_time, compute_scatter_travel_time


def _params():
    return args_to_params(
        parse_arguments(
            [
                "--fiber-channel-count",
                "8",
                "--source-shot-count",
                "2",
                "--time-record-length-s",
                "0.18",
                "--gauge-length-m",
                "4",
                "--scan-x-min-m",
                "56",
                "--scan-x-max-m",
                "60",
                "--scan-x-step-m",
                "2",
                "--scan-y-min-m",
                "8",
                "--scan-y-max-m",
                "10",
                "--scan-y-step-m",
                "1",
                "--scan-depth-min-m",
                "2",
                "--scan-depth-max-m",
                "3",
                "--scan-depth-step-m",
                "1",
            ]
        )
    )


def test_observation_kernel_shape_and_shared_travel_times():
    params = _params()
    source_xyz = generate_source_xyz(params)
    receiver_xyz = generate_receiver_xyz(params)
    candidate_xyz = candidate_grid_to_xyz(
        params.derived.scan_x_grid,
        params.derived.scan_y_grid,
        params.derived.scan_depth_grid,
    )
    velocity_model = build_velocity_model(params)
    attenuation_model = build_attenuation_model(params)

    paths = build_observation_paths_3d(source_xyz, receiver_xyz, candidate_xyz, velocity_model, attenuation_model, params)

    assert paths.scatter_time_s.shape == (source_xyz.shape[0], receiver_xyz.shape[0], candidate_xyz.shape[0])
    assert paths.metadata["uses_velocity_path_integration"] is True
    assert paths.metadata["uses_receiver_consistent_paths"] is True
    expected_direct = params.time.t0_s + compute_kinematic_travel_time(source_xyz[0], receiver_xyz[0], velocity_model)
    expected_scatter = params.time.t0_s + compute_scatter_travel_time(
        source_xyz[:1], candidate_xyz[:1], receiver_xyz[:1], velocity_model
    )[0, 0, 0]
    assert np.isclose(paths.direct_time_s[0, 0, 0], expected_direct)
    assert np.isclose(paths.scatter_time_s[0, 0, 0], expected_scatter)


def test_kernel_based_synthesis_outputs_gather_shape():
    params = _params()
    source_xyz = generate_source_xyz(params)
    receiver_xyz = generate_receiver_xyz(params)
    candidate_xyz = np.array([[params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m]], dtype=float)
    paths = build_observation_paths_3d(
        source_xyz,
        receiver_xyz,
        candidate_xyz,
        build_velocity_model(params),
        build_attenuation_model(params),
        params,
        candidate_weight=np.array([params.anomaly.scatter_strength], dtype=float),
    )

    result = synthesize_gather_from_observation_paths(params, paths)

    assert result["synthetic_data"].shape == (params.source.shot_count, params.derived.nt, params.fiber.channel_count)
    assert np.max(np.abs(result["synthetic_data"])) > 0.0
