import numpy as np

from main import args_to_params, parse_arguments
from src.forward.observation_kernel_3d import build_observation_paths_3d, candidate_grid_to_xyz, synthesize_gather_from_observation_paths
from src.geometry.acquisition_geometry import generate_receiver_xyz, generate_source_xyz
from src.localization.receiver_consistent_imaging import build_receiver_consistent_imaging_volume
from src.model.attenuation_model import build_attenuation_model
from src.model.velocity_model import build_velocity_model


def _params():
    return args_to_params(
        parse_arguments(
            [
                "--fiber-channel-count",
                "9",
                "--source-shot-count",
                "2",
                "--time-record-length-s",
                "0.45",
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
                "4",
                "--scan-depth-step-m",
                "1",
            ]
        )
    )


def test_receiver_consistent_imaging_volume_uses_kernel_paths():
    params = _params()
    source_xyz = generate_source_xyz(params)
    receiver_xyz = generate_receiver_xyz(params)
    candidate_xyz = candidate_grid_to_xyz(
        params.derived.scan_x_grid,
        params.derived.scan_y_grid,
        params.derived.scan_depth_grid,
    )
    paths = build_observation_paths_3d(
        source_xyz,
        receiver_xyz,
        candidate_xyz,
        build_velocity_model(params),
        build_attenuation_model(params),
        params,
    )
    anomaly_candidate = np.array([[params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m]], dtype=float)
    anomaly_paths = build_observation_paths_3d(
        source_xyz,
        receiver_xyz,
        anomaly_candidate,
        build_velocity_model(params),
        build_attenuation_model(params),
        params,
        candidate_weight=np.array([params.anomaly.scatter_strength], dtype=float),
    )
    gather = synthesize_gather_from_observation_paths(params, anomaly_paths)["synthetic_data"]

    result = build_receiver_consistent_imaging_volume(
        paths,
        gather,
        params.derived.time_axis,
        params.derived.scan_x_grid,
        params.derived.scan_y_grid,
        params.derived.scan_depth_grid,
        truth_location={"x_m": params.anomaly.x0_m, "y_m": params.anomaly.y0_m, "depth_m": params.anomaly.depth_m},
    )

    expected_shape = (
        len(params.derived.scan_x_grid),
        len(params.derived.scan_y_grid),
        len(params.derived.scan_depth_grid),
    )
    assert result["imaging_volume_combined"].shape == expected_shape
    assert result["imaging_metadata"]["imaging_uses_receiver_consistent_paths"] is True
    assert result["imaging_metadata"]["imaging_uses_observation_kernel"] is True
    assert result["imaging_metadata"]["volume_proxy_used_for_localization"] is False
    assert result["imaging_peak_location"]
    assert np.max(result["imaging_volume_combined"]) > 0.0
