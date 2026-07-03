import numpy as np

from main import args_to_params, parse_arguments
from src.forward.direct_wave import simulate_direct_wave
from src.forward.forward_registry import run_registered_forward
from src.forward.scatter_kinematic import simulate_scatter_wave
from src.geometry.acquisition_geometry import generate_receiver_xyz, generate_source_xyz
from src.model.anomalies import anomaly_to_scatter_points, build_anomaly_from_params
from src.model.velocity_model import build_velocity_model


def _params(model_type: str = "layered"):
    return args_to_params(
        parse_arguments(
            [
                "--velocity-model-type",
                model_type,
                "--fiber-channel-count",
                "14",
                "--source-shot-count",
                "2",
                "--time-record-length-s",
                "0.2",
                "--save-figures",
                "false",
            ]
        )
    )


def _geometry(params):
    receiver_xyz = generate_receiver_xyz(params)
    source_xyz = generate_source_xyz(params)
    anomaly = build_anomaly_from_params(params)
    scatter_xyz, scatter_weight = anomaly_to_scatter_points(anomaly, params.anomaly.scatter_point_mode)
    return source_xyz, receiver_xyz, scatter_xyz, scatter_weight


def test_direct_and_scatter_wave_accept_velocity_model_object():
    params = _params("layered")
    source_xyz, receiver_xyz, scatter_xyz, scatter_weight = _geometry(params)
    velocity_model = build_velocity_model(params)

    direct = simulate_direct_wave(params, source_xyz, receiver_xyz, velocity_model)
    scatter = simulate_scatter_wave(params, source_xyz, receiver_xyz, scatter_xyz, scatter_weight, velocity_model)

    assert direct.shape == scatter.shape
    assert direct.shape == (params.source.shot_count, params.derived.nt, params.fiber.channel_count)
    assert velocity_model.model_type == "layered"


def test_registered_layered_forward_differs_from_uniform_forward():
    layered_params = _params("layered")
    source_xyz, receiver_xyz, scatter_xyz, scatter_weight = _geometry(layered_params)
    uniform_params = _params("uniform")
    uniform_params.forward.engine = "kinematic_baseline"

    layered = run_registered_forward(layered_params, source_xyz, receiver_xyz, scatter_xyz, scatter_weight)
    uniform = run_registered_forward(uniform_params, source_xyz, receiver_xyz, scatter_xyz, scatter_weight)

    assert layered["forward_engine"] == "layered_kinematic"
    assert uniform["forward_engine"] == "kinematic_baseline"
    assert layered["synthetic_data"].shape == uniform["synthetic_data"].shape
    assert not np.allclose(layered["synthetic_data"], uniform["synthetic_data"])
