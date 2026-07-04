from pathlib import Path
import sys

CODE_DIR = str(Path("code").resolve())
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from current_3d_algorithm.stable_forward import STABLE_FORWARD_ENGINE
from src.forward.forward_registry import list_forward_engines


def test_forward_module_inventory_docs_exist():
    assert Path("src/forward/README.md").exists()
    assert Path("docs/forward_module_inventory.md").exists()


def test_forward_registry_lists_active_baseline_and_validation_engines():
    engines = list_forward_engines()
    assert "kinematic_baseline" in engines
    assert "layered_kinematic" in engines
    assert "acoustic2d_prototype" in engines
    assert "elastic2d_prototype" in engines
    assert STABLE_FORWARD_ENGINE == "layered_kinematic"


def test_legacy_forward_files_are_not_marked_active():
    text = Path("docs/forward_module_inventory.md").read_text(encoding="utf-8")
    assert "`src/forward/direct_wave.py` | 直达波运动学基础组件" in text
    assert "`src/forward/scatter_kinematic.py` | 等效散射运动学基础组件" in text
    active_section = Path("src/forward/README.md").read_text(encoding="utf-8")
    assert "当前 active engine" in active_section
    assert "layered_kinematic.py" in active_section
    assert "direct_wave.py`：直达波运动学基础组件" in active_section
