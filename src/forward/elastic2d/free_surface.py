"""elastic2d free-surface 模式说明。"""

from __future__ import annotations


FREE_SURFACE_MODES = {
    "approximate": "最小 traction-free 近似，只在顶部应力点置零。",
    "stress_zero_variant": "浅层两排应力置零，用于检查自由表面对拾取的敏感性。",
    "traction_free_variant": "staggered-grid benchmark 中的最小 traction-free variant。",
}


def describe_free_surface_mode(mode: str) -> str:
    """返回 free-surface 模式说明。"""

    return FREE_SURFACE_MODES.get(mode, "未知 free-surface 模式。")
