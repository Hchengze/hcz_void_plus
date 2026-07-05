import numpy as np

from src.localization.posterior_volume import build_posterior_from_score
from src.localization.uncertainty_volume import high_probability_region, summarize_uncertainty_volume


def test_uncertainty_volume_reports_high_probability_region_and_axes():
    score = np.zeros((4, 3, 2), dtype=float)
    score[1, 1, 0] = 4.0
    posterior = build_posterior_from_score(score, np.arange(4.0), np.arange(3.0), np.array([1.0, 2.0]))
    region = high_probability_region(
        posterior["posterior_probability_volume"],
        np.arange(4.0),
        np.arange(3.0),
        np.array([1.0, 2.0]),
        mass_threshold=0.8,
    )
    summary = summarize_uncertainty_volume(posterior["posterior_summary"], region)
    assert region["point_count"] >= 1
    assert "connected_components_3d" in summary
    assert np.asarray(summary["uncertainty_ellipsoid_axes"]).shape == (3,)
    assert summary["recommended_location_type"] == "posterior_peak_with_uncertainty_region"
