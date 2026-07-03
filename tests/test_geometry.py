import numpy as np

from main import args_to_params, parse_arguments
from src.geometry.acquisition_geometry import generate_receiver_xyz, generate_source_xyz
from src.geometry.distance import source_receiver_distance, source_scatter_receiver_path_distance


def test_geometry_shapes_and_distances_are_reasonable():
    params = args_to_params(
        parse_arguments(
            [
                "--fiber-channel-count",
                "12",
                "--source-shot-count",
                "2",
                "--road-width-m",
                "10",
                "--gauge-length-m",
                "4",
            ]
        )
    )
    receiver_xyz = generate_receiver_xyz(params)
    source_xyz = generate_source_xyz(params)
    direct = source_receiver_distance(source_xyz, receiver_xyz)

    assert receiver_xyz.shape == (12, 3)
    assert source_xyz.shape == (2, 3)
    assert direct.shape == (2, 12)
    assert np.all(direct > 0)

    scatter_xyz = np.array([[5.0, 4.0, 3.0]], dtype=float)
    scatter_path = source_scatter_receiver_path_distance(source_xyz, scatter_xyz, receiver_xyz)

    assert scatter_path.shape == (2, 1, 12)
    assert np.all(scatter_path[:, 0, :] >= direct)
