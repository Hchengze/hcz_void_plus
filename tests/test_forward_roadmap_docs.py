from pathlib import Path
import sys

CODE_DIR = str(Path("code").resolve())
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from current_3d_algorithm.stable_api import get_current_algorithm_summary


def test_forward_roadmap_docs_exist_and_include_f0_f6():
    roadmap = Path("docs/forward_modeling_roadmap.md")
    boundary = Path("docs/forward_modeling_boundary.md")
    matrix = Path("docs/forward_modeling_reference_matrix.md")
    elastic_design = Path("docs/elastic2d_forward_design.md")
    for path in [roadmap, boundary, matrix, elastic_design]:
        assert path.exists()
    text = roadmap.read_text(encoding="utf-8")
    for stage in ["F0", "F1", "F2", "F3", "F4", "F5", "F6"]:
        assert stage in text
    assert "acoustic2d_prototype" in text
    assert "elastic2d" in text


def test_stable_api_returns_forward_roadmap():
    summary = get_current_algorithm_summary()
    assert summary["stage"] == "Stage 5D"
    assert summary["stable_forward_engine"] == "layered_kinematic"
    assert "acoustic2d_prototype" in summary["available_validation_forward"]
    assert "elastic2d_prototype" in summary["available_validation_forward"]
    assert summary["planned_physics_forward"] == "elastic2d accuracy/stability hardening + 2.5D multi-section validation"
    assert "F6" in summary["forward_roadmap"]
