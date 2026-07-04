import numpy as np

from main import args_to_params, parse_arguments
from src.visualization.plot_localization_3d import (
    plot_3d_high_score_region,
    plot_3d_uncertainty_box,
    plot_recommended_location_3d,
)


def test_localization_3d_plotting_functions_run(tmp_path):
    params = args_to_params(parse_arguments([]))
    shape = (
        len(params.derived.scan_x_grid),
        len(params.derived.scan_y_grid),
        len(params.derived.scan_depth_grid),
    )
    score = np.zeros(shape, dtype=float)
    score[shape[0] // 2, shape[1] // 2, shape[2] // 2] = 1.0
    location = {"x_m": params.anomaly.x0_m, "y_m": params.anomaly.y0_m, "depth_m": params.anomaly.depth_m}
    confidence = {
        "high_score_region": {
            "threshold_ratio": 0.9,
            "x_span_m": 1.0,
            "y_span_m": 1.0,
            "depth_span_m": 1.0,
            "equivalent_uncertainty_box": {"x_span_m": 1.0, "y_span_m": 1.0, "depth_span_m": 1.0},
        },
        "recommended_location": location,
    }
    scan_result = {"best_location": location}
    plot_3d_high_score_region(params, score, confidence, scan_result, tmp_path / "fig_3d_high_score_region.png")
    plot_recommended_location_3d(params, confidence, scan_result, tmp_path / "fig_recommended_location_3d.png")
    plot_3d_uncertainty_box(params, confidence, tmp_path / "fig_3d_uncertainty_box.png")
    assert (tmp_path / "fig_3d_high_score_region.png").exists()
    assert (tmp_path / "fig_recommended_location_3d.png").exists()
    assert (tmp_path / "fig_3d_uncertainty_box.png").exists()
