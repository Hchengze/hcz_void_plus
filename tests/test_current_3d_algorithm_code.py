from pathlib import Path
import sys

CODE_DIR = str(Path("code").resolve())
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from current_3d_algorithm.stable_api import get_current_algorithm_summary
from current_3d_algorithm.stable_pipeline import smoke_current_pipeline


def test_current_3d_algorithm_directory_exists():
    stable_dir = Path("code/current_3d_algorithm")
    assert stable_dir.exists()
    assert any(path.name != ".gitkeep" for path in stable_dir.iterdir())


def test_stable_api_reports_current_algorithm_line():
    summary = get_current_algorithm_summary()
    assert summary["stage"] == "Stage 5B"
    assert summary["velocity_default"] == "layered"
    assert summary["main_localization"] == "multi_attribute_unweighted"
    assert summary["stable_forward_engine"] == "layered_kinematic"
    assert summary["planned_physics_forward"] == "elastic2d"
    assert summary["not_engineering_diagnosis"] is True


def test_stable_pipeline_smoke_params_can_build():
    smoke = smoke_current_pipeline()
    params = smoke["params"]
    assert params.project.task == "full_pipeline"
    assert params.velocity.model_type == "layered"
    assert params.output.export_latest_stable is False


def test_algorithm_overview_documents_stable_line():
    text = Path("code/current_3d_algorithm/algorithm_overview.md").read_text(encoding="utf-8")
    assert "multi_attribute" in text
    assert "layered" in text
    assert "uncertainty" in text
    assert "layered_kinematic" in text
    assert "acoustic2d_prototype" in text
