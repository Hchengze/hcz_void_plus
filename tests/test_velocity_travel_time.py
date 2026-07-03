import numpy as np

from src.model.layered_velocity import LayeredVelocityModel
from src.model.velocity_model import (
    UniformVelocityModel,
    compute_kinematic_travel_time,
    compute_scatter_travel_time,
)


def test_layered_travel_time_differs_from_uniform():
    start = np.array([0.0, 0.0, 0.0])
    end = np.array([0.0, 0.0, 4.0])
    uniform = UniformVelocityModel(200.0)
    layered = LayeredVelocityModel(
        layer_depths_m=np.array([1.0, 5.0]),
        layer_rayleigh_velocities_mps=np.array([100.0, 200.0]),
        reference_velocity_mps=200.0,
    )
    t_uniform = compute_kinematic_travel_time(start, end, uniform)
    t_layered = compute_kinematic_travel_time(start, end, layered)
    assert abs(float(t_uniform) - float(t_layered)) > 1.0e-4


def test_compute_scatter_travel_time_shape():
    source = np.array([[0.0, 0.0, 0.0], [10.0, 0.0, 0.0]])
    receiver = np.array([[0.0, 5.0, 0.0], [10.0, 5.0, 0.0], [20.0, 5.0, 0.0]])
    scatter = np.array([[5.0, 2.5, 2.0]])
    model = UniformVelocityModel(250.0)
    travel_time = compute_scatter_travel_time(source, scatter, receiver, model)
    assert travel_time.shape == (2, 1, 3)
    assert np.all(travel_time > 0.0)
