import numpy as np

from src.forward.elastic2d.das_response import build_elastic_das_response


def test_elastic2d_das_response_shapes_are_reasonable():
    time_count = 20
    channel_count = 15
    surface_vx = np.tile(np.linspace(0.0, 1.0, channel_count), (time_count, 1))
    surface_vz = np.ones((time_count, channel_count))
    response = build_elastic_das_response(surface_vx, surface_vz, dx_m=0.5, gauge_length_m=2.0)
    assert response["point_receiver_gather"].shape == (time_count, channel_count)
    assert response["gauge_length_strain_gather"].shape == (time_count, channel_count)
    assert np.max(np.abs(response["gauge_length_strain_gather"])) > 0.0
