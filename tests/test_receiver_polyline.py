from pathlib import Path

from main import args_to_params, parse_arguments
from src.geometry.receiver_polyline import build_receiver_xyz


def test_receiver_polyline_csv_generates_xyz(tmp_path):
    csv_path = tmp_path / "receiver.csv"
    csv_path.write_text("x_m,y_m,z_m\n0,0,0\n1,0.5,0.1\n", encoding="utf-8")
    params = args_to_params(parse_arguments(["--receiver-geometry-mode", "polyline_csv", "--receiver-polyline-csv", str(csv_path)]))
    receiver_xyz = build_receiver_xyz(params)
    assert receiver_xyz.shape == (2, 3)

