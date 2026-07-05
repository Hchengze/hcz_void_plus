import json
from pathlib import Path

import sys

CODE_DIR = str(Path("code").resolve())
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from current_3d_algorithm.stable_api import get_current_algorithm_summary


def test_stage5j_is_declared_in_all_current_entrypoints():
    files = [
        Path("README.md"),
        Path("docs/current_status.md"),
        Path("docs/current_algorithm_boundary.md"),
        Path("code/current_3d_algorithm/README.md"),
    ]
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert "Stage 5J" in text
        assert "layered_kinematic" in text

    summary = get_current_algorithm_summary()
    assert summary["stage"] == "Stage 5J"
    assert summary["velocity_default"] == "layered"
    assert summary["stable_forward_engine"] == "layered_kinematic"
    assert summary["ready_for_2p5d"] is False


def test_latest_stable_summary_stage5j_after_refresh():
    summary_path = Path("outputs/latest_stable/summary.md")
    assert summary_path.exists()
    text = summary_path.read_text(encoding="utf-8")
    assert "Stage 5J" in text
    assert "previous_stage = Stage 5I" in text
    assert "algorithm_commit" in text
    assert "latest_stable_commit" in text
    assert "active_velocity_model" in text
    assert "ready_for_2p5d" in text
    assert "manual_review_figures" in text
    if "rayleigh_like_event_detected：`False`" in text or "rayleigh_like_event_detected：`False`" in text:
        assert "ready_for_2p5d = `False`" in text or "ready_for_2p5d：`False`" in text


def test_latest_stable_metadata_records_stage5j():
    meta_path = Path("outputs/latest_stable/metadata/meta_run.json")
    assert meta_path.exists()
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    assert metadata["stage"] == "Stage 5J 3D kinematic forward volume and attenuation modeling"
    assert metadata["algorithm_commit"]
    assert "latest_stable_commit" in metadata
    assert metadata["approximation"]["forward_engine"] == "layered_kinematic"
    assert metadata["stage5f_validation"]["ready_for_2p5d"] is False
    assert metadata["stage5h_validation"]["ready_for_2p5d"] is False
    assert metadata["stage5i_validation"]["ready_for_2p5d"] is False
    assert metadata["stage5j_validation"]["ready_for_2p5d"] is False
    assert metadata["stage5g_validation"]["latest_stable_categories"] == [
        "forward",
        "localization",
        "error_analysis",
    ]
