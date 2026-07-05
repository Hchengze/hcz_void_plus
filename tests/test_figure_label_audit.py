from pathlib import Path

from src.validation.figure_label_audit import run_figure_label_audit
from src.visualization.label_i18n import zh_label


def test_case_label_mapping_contains_stage5h_required_labels():
    assert zh_label("collocated_vertical") == "共点网格-垂向力源"
    assert zh_label("collocated_horizontal") == "共点网格-水平力源"
    assert zh_label("staggered_vertical") == "错格网格-垂向力源"
    assert zh_label("staggered_horizontal") == "错格网格-水平力源"
    assert zh_label("staggered_traction_variant") == "错格网格-自由面变体"
    assert zh_label("horizontal_force") == "水平力源"
    assert zh_label("vertical_force") == "垂向力源"
    assert zh_label("explosive") == "爆炸源近似"


def test_latest_stable_figure_label_audit_passes_after_export():
    result = run_figure_label_audit(Path("outputs/latest_stable"))
    assert result["stage"] == "Stage 5H"
    assert result["status"] == "pass"
    assert result["english_case_label_count"] == 0
