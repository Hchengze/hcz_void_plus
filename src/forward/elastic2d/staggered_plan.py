"""elastic2d staggered-grid 最小规划结构。

Stage 5E 不把 staggered-grid 写成成熟求解器。本模块只固化网格布局、CFL 检查
和更新公式占位，目的是让后续实现有清晰的物理变量位置，而不是继续在
collocated-grid 上盲目调参。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class StaggeredElastic2DLayout:
    """staggered-grid velocity-stress 变量布局说明。"""

    nx: int
    nz: int
    dx_m: float
    dz_m: float
    vx_shape: tuple[int, int]
    vz_shape: tuple[int, int]
    normal_stress_shape: tuple[int, int]
    shear_stress_shape: tuple[int, int]
    note: str


def build_staggered_layout(nx: int, nz: int, dx_m: float, dz_m: float) -> StaggeredElastic2DLayout:
    """生成最小 staggered-grid 变量 shape。

    这里仅描述位置关系，不做时间推进。vx/vz 与应力网格错半格，有助于后续实现
    更稳定的 velocity-stress 弹性方程。
    """

    if nx < 4 or nz < 4:
        raise ValueError("staggered-grid 至少需要 4×4 网格。")
    if dx_m <= 0.0 or dz_m <= 0.0:
        raise ValueError("staggered-grid 网格间距必须为正。")
    return StaggeredElastic2DLayout(
        nx=nx,
        nz=nz,
        dx_m=float(dx_m),
        dz_m=float(dz_m),
        vx_shape=(nz, nx + 1),
        vz_shape=(nz + 1, nx),
        normal_stress_shape=(nz, nx),
        shear_stress_shape=(nz + 1, nx + 1),
        note="Stage 5E 只提供布局与检查，不提供成熟 staggered-grid 时间推进。",
    )


def check_staggered_cfl(vp_mps: float, dt_s: float, dx_m: float, dz_m: float, safety: float = 0.45) -> dict[str, Any]:
    """检查 staggered-grid 弹性 FDTD 的保守 CFL 条件。"""

    limit = safety / (float(vp_mps) * np.sqrt(1.0 / dx_m**2 + 1.0 / dz_m**2))
    return {
        "dt_s": float(dt_s),
        "dt_limit_s": float(limit),
        "stable": bool(dt_s <= limit),
        "safety": float(safety),
    }


def describe_staggered_update_placeholders() -> list[str]:
    """返回后续需要实现的 staggered-grid 更新公式清单。"""

    return [
        "vx 半步更新：由 sxx 的 x 导数与 sxz 的 z 导数驱动。",
        "vz 半步更新：由 sxz 的 x 导数与 szz 的 z 导数驱动。",
        "sxx/szz 整步更新：由 vx/vz 散度和 Lamé 参数驱动。",
        "sxz 整步更新：由 vx_z 与 vz_x 剪切应变率驱动。",
        "free surface：需要在 staggered 应力点上严格满足 szz=0 与 sxz=0。",
        "absorbing boundary：应从 sponge 升级到 PML 或 split-field PML。",
    ]
