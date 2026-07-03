from main import args_to_params, parse_arguments
from src.model.anomalies import anomaly_to_scatter_points, build_anomaly_from_params


def test_anomaly_shapes_generate_3d_scatter_points():
    for shape in ["sphere", "ellipsoid", "box", "cylinder", "pipe_trench"]:
        params = args_to_params(parse_arguments(["--anomaly-shape", shape, "--scatter-point-density", "coarse"]))
        anomaly = build_anomaly_from_params(params)
        scatter_xyz, weight = anomaly_to_scatter_points(anomaly, "center_and_boundary")
        assert scatter_xyz.ndim == 2
        assert scatter_xyz.shape[1] == 3
        assert scatter_xyz.shape[0] == weight.shape[0]

