import numpy as np

from main import args_to_params, parse_arguments
from src.forward.kinematic_baseline import run_kinematic_baseline_forward
from src.forward.layered_kinematic import run_layered_kinematic_forward
from src.geometry.acquisition_geometry import generate_receiver_xyz, generate_source_xyz
from src.model.anomalies import anomaly_to_scatter_points, build_anomaly_from_params


def _small_params():
    return args_to_params(
        parse_arguments(
            [
                "--fiber-channel-count",
                "16",
                "--source-shot-count",
                "2",
                "--time-record-length-s",
                "0.22",
                "--save-figures",
                "false",
            ]
        )
    )


def test_layered_kinematic_forward_differs_from_uniform_baseline():
    params = _small_params()
    receiver_xyz = generate_receiver_xyz(params)
    source_xyz = generate_source_xyz(params)
    anomaly = build_anomaly_from_params(params)
    scatter_xyz, scatter_weight = anomaly_to_scatter_points(anomaly, params.anomaly.scatter_point_mode)

    baseline = run_kinematic_baseline_forward(params, source_xyz, receiver_xyz, scatter_xyz, scatter_weight)
    layered = run_layered_kinematic_forward(params, source_xyz, receiver_xyz, scatter_xyz, scatter_weight)

    assert baseline["synthetic_data"].shape == layered["synthetic_data"].shape
    assert baseline["forward_engine"] == "kinematic_baseline"
    assert layered["forward_engine"] == "layered_kinematic"
    assert layered["velocity_model"].model_type == "layered"
    assert not np.allclose(baseline["synthetic_data"], layered["synthetic_data"])
