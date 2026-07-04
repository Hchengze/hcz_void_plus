"""elastic2d absorbing boundary 模式说明。"""

from __future__ import annotations


BOUNDARY_MODES = {
    "sponge_weak": "弱 sponge，边界反射可能较强。",
    "sponge_medium": "默认 sponge，用于小网格 validation。",
    "sponge_strong": "强 sponge，可能压制近地表弱事件。",
    "minimal_pml_plan": "PML 设计占位，本轮不作为成熟实现。",
}


def describe_boundary_mode(mode: str) -> str:
    """返回 absorbing boundary 模式说明。"""

    return BOUNDARY_MODES.get(mode, "未知 absorbing boundary 模式。")
