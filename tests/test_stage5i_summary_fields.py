from pathlib import Path


def test_latest_stable_summary_contains_stage5i_algorithm_fields():
    summary = Path("outputs/latest_stable/summary.md")
    assert summary.exists()
    text = summary.read_text(encoding="utf-8")
    assert "Stage 5I" in text
    for field in [
        "scan_candidate_uses_path_integration",
        "scan_uses_representative_velocity",
        "multi_attribute_inversion_enabled",
        "posterior_volume_status",
        "posterior_peak_location",
        "posterior_mean_location",
        "posterior_uncertainty_axes",
        "geometry_resolution_status",
        "ambiguity_warning",
        "ready_for_2p5d",
    ]:
        assert field in text
