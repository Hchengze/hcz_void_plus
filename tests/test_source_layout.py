from main import args_to_params, parse_arguments
from src.geometry.source_layout import build_source_xyz


def test_source_grid_and_csv_generate_xyz(tmp_path):
    params = args_to_params(parse_arguments(["--source-geometry-mode", "grid", "--source-shot-count", "4"]))
    source_xyz = build_source_xyz(params)
    assert source_xyz.shape == (4, 3)

    csv_path = tmp_path / "source.csv"
    csv_path.write_text("x_m,y_m,z_m\n0,18,0\n1,18,0\n", encoding="utf-8")
    params_csv = args_to_params(parse_arguments(["--source-geometry-mode", "csv", "--source-points-csv", str(csv_path)]))
    source_csv = build_source_xyz(params_csv)
    assert source_csv.shape == (2, 3)

