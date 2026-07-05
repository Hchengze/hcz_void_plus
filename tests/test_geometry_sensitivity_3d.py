import numpy as np

from src.localization.aperture_metrics import summarize_aperture
from src.localization.geometry_sensitivity import compute_geometry_resolution_volume


def test_aperture_metrics_are_finite_for_3d_candidate():
    source = np.array([[0.0, 20.0, 0.0], [20.0, 20.0, 0.0]])
    receiver = np.array([[0.0, 0.0, 0.0], [20.0, 0.0, 0.0]])
    metrics = summarize_aperture(source, receiver, np.array([10.0, 10.0, 3.0]))
    assert metrics["candidate_illumination_count"] > 0
    assert 0.0 <= metrics["lateral_ambiguity_index"] <= 1.0
    assert 0.0 <= metrics["depth_ambiguity_index"] <= 1.0


def test_geometry_resolution_volume_shape_and_summary():
    source = np.array([[0.0, 20.0, 0.0], [20.0, 20.0, 0.0]])
    receiver = np.array([[0.0, 0.0, 0.0], [20.0, 0.0, 0.0]])
    result = compute_geometry_resolution_volume(
        source,
        receiver,
        np.array([0.0, 10.0]),
        np.array([5.0, 10.0]),
        np.array([1.0, 3.0]),
    )
    assert result["geometry_resolution_volume"].shape == (2, 2, 2)
    assert result["geometry_resolution_status"] == "computed"
    assert "y_depth_separable" in result["geometry_resolution_summary"]
