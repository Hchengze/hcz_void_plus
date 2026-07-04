"""elastic2d 占位状态。

该文件故意不实现 elastic2d 数值求解器。Stage 5B 的目标是把技术路线写清楚，
并阻止后续把 acoustic2d prototype 或 straight-ray kinematic approximation
误写成 Rayleigh/free-surface/void scattering 全波场。
"""

from __future__ import annotations


def elastic2d_status() -> dict[str, object]:
    """返回 elastic2d 当前状态。

    返回值用于测试和 stable API。中文字段明确说明当前只是设计阶段，下一步才会
    进入局部 2D elastic velocity-stress FDTD prototype。
    """

    return {
        "stage": "F3",
        "status": "minimal_prototype_available",
        "next_required": "elastic2d accuracy/stability hardening",
        "purpose": "Rayleigh/free-surface/void scattering 局部全波场验证",
        "implemented_solver": True,
    }
