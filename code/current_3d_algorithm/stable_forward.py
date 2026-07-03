"""稳定 forward 主线入口。

本文件只暴露当前稳定 forward 主线，不复制研发区实现。Stage 5B 后，默认稳定
正演是 `layered_kinematic`；`acoustic2d_prototype` 只作为 validation forward，
不能作为 DAS-like Rayleigh 主定位数据。
"""

from __future__ import annotations

from src.forward.forward_registry import get_forward_engine_spec, list_forward_engines, run_registered_forward
from src.forward.layered_kinematic import run_layered_kinematic_forward


STABLE_FORWARD_ENGINE = "layered_kinematic"
AVAILABLE_VALIDATION_FORWARD = "acoustic2d_prototype"
PLANNED_PHYSICS_FORWARD = "elastic2d"


def get_stable_forward_summary() -> dict[str, object]:
    """返回当前稳定 forward 主线说明。"""

    return {
        "stable_forward_engine": STABLE_FORWARD_ENGINE,
        "available_validation_forward": AVAILABLE_VALIDATION_FORWARD,
        "planned_physics_forward": PLANNED_PHYSICS_FORWARD,
        "available_forward_engines": list_forward_engines(),
        "stable_forward_spec": get_forward_engine_spec(STABLE_FORWARD_ENGINE).description,
        "boundary": "layered_kinematic 是 straight-ray kinematic approximation，不是 3D elastic wavefield。",
    }


__all__ = [
    "AVAILABLE_VALIDATION_FORWARD",
    "PLANNED_PHYSICS_FORWARD",
    "STABLE_FORWARD_ENGINE",
    "get_stable_forward_summary",
    "run_layered_kinematic_forward",
    "run_registered_forward",
]
