import json
from pathlib import Path

import sys

CODE_DIR = str(Path("code").resolve())
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from current_3d_algorithm.stable_api import get_current_algorithm_summary


def test_stage5f_is_declared_in_all_current_entrypoints():
    files = [
        Path("README.md"),
        Path("docs/current_status.md"),
        Path("docs/current_algorithm_boundary.md"),
        Path("code/current_3d_algorithm/README.md"),
    ]
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert "Stage 5F" in text
        assert "layered_kinematic" in text

    summary = get_current_algorithm_summary()
    assert summary["stage"] == "Stage 5F"
    assert summary["velocity_default"] == "layered"
    assert summary["stable_forward_engine"] == "layered_kinematic"
    assert summary["ready_for_2p5d"] is False


def test_latest_stable_summary_stage5f_after_refresh():
    summary_path = Path("outputs/latest_stable/summary.md")
    assert summary_path.exists()
    text = summary_path.read_text(encoding="utf-8")
    assert "stage：`Stage 5F`" in text or "Stage 5F" in text
    assert "active_velocity_model_type" in text
    assert "ready_for_2p5d" in text
    if "rayleigh_like_event_detected：`False`" in text:
        assert "ready_for_2p5d：`False`" in text


def test_latest_stable_metadata_records_stage5f():
    meta_path = Path("outputs/latest_stable/metadata/meta_run.json")
    assert meta_path.exists()
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    assert metadata["stage"] == "Stage 5F curated figure governance and staggered elastic2d benchmark"
    assert metadata["approximation"]["forward_engine"] == "layered_kinematic"
    assert metadata["stage5f_validation"]["ready_for_2p5d"] is False
