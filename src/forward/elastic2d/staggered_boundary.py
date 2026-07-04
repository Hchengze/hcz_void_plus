"""staggered-grid elastic2d 边界处理。"""

from __future__ import annotations

import numpy as np

from src.forward.elastic2d.staggered_grid import StaggeredGrid2D


def build_staggered_sponge(grid: StaggeredGrid2D, mode: str = "medium") -> dict[str, np.ndarray]:
    """构建 vx/vz/stress 对应的 sponge 衰减矩阵。"""

    strength = {"weak": 0.006, "medium": 0.015, "strong": 0.035}.get(mode, 0.015)
    width = max(4, min(grid.nx, grid.nz) // 8)

    def damping(shape: tuple[int, int]) -> np.ndarray:
        arr = np.ones(shape, dtype=float)
        nz, nx = shape
        for iz in range(nz):
            for ix in range(nx):
                dist = min(ix, nx - 1 - ix, nz - 1 - iz)
                if iz <= 1:
                    dist = width
                if dist < width:
                    arr[iz, ix] = np.exp(-strength * (width - dist) ** 2)
        return arr

    return {
        "stress": damping((grid.nz, grid.nx)),
        "vx": damping((grid.nz, grid.nx + 1)),
        "vz": damping((grid.nz + 1, grid.nx)),
        "sxz": damping((grid.nz + 1, grid.nx + 1)),
    }


def apply_staggered_free_surface(szz: np.ndarray, sxz: np.ndarray, mode: str) -> None:
    """施加最小 traction-free 近似。"""

    if mode == "traction_free_variant":
        szz[:2, :] = 0.0
        sxz[:2, :] = 0.0
    else:
        szz[0, :] = 0.0
        sxz[0, :] = 0.0
