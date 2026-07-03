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


def test_default_single_sided_geometry_lines_are_on_opposite_road_sides():
    params = args_to_params(
        parse_arguments(
            [
                "--road-width-m",
                "18",
                "--fiber-channel-count",
                "20",
                "--source-shot-count",
                "3",
                "--gauge-length-m",
                "4",
            ]
        )
    )
    receiver_xyz = generate_receiver_xyz(params)
    source_xyz = generate_source_xyz(params)

    assert params.source.y_m == params.road.width_m
    assert np.all(receiver_xyz[:, 1] == params.fiber.y_m)
    assert np.all(source_xyz[:, 1] == params.source.y_m)
    assert params.fiber.y_m == 0.0
    assert params.source.y_m != params.fiber.y_m
    assert 0.0 <= params.anomaly.y0_m <= params.road.width_m
