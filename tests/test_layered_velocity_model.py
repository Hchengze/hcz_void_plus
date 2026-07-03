import numpy as np

from main import args_to_params, parse_arguments
from src.model.layered_velocity import LayeredVelocityModel
from src.model.velocity_model import build_velocity_model


def test_default_velocity_model_is_layered():
    params = args_to_params(parse_arguments([]))
    assert params.velocity.model_type == "layered"
    model = build_velocity_model(params)
    assert model.model_type == "layered"


def test_layered_velocity_changes_with_depth():
    model = LayeredVelocityModel(
        layer_depths_m=np.array([0.5, 2.0, 5.0]),
        layer_rayleigh_velocities_mps=np.array([120.0, 200.0, 320.0]),
        reference_velocity_mps=220.0,
    )
    xyz = np.array([[0.0, 0.0, 0.2], [0.0, 0.0, 1.0], [0.0, 0.0, 4.0]])
    assert np.allclose(model.velocity_at(xyz), [120.0, 200.0, 320.0])
