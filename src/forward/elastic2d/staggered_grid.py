"""elastic2d staggered-grid 变量布局。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class StaggeredGrid2D:
    """二维 velocity-stress staggered-grid。

    变量位置：
        sxx/szz 位于 cell center，shape=(nz, nx)；
        vx 位于 x-face，shape=(nz, nx+1)；
        vz 位于 z-face，shape=(nz+1, nx)；
        sxz 位于 cell corner，shape=(nz+1, nx+1)。
    """

    nx: int
    nz: int
    dx_m: float
    dz_m: float

    @property
    def x_m(self) -> np.ndarray:
        return np.arange(self.nx, dtype=float) * self.dx_m

    @property
    def z_m(self) -> np.ndarray:
        return np.arange(self.nz, dtype=float) * self.dz_m

    @property
    def width_m(self) -> float:
        return (self.nx - 1) * self.dx_m

    @property
    def depth_m(self) -> float:
        return (self.nz - 1) * self.dz_m


def build_staggered_grid_from_params(params) -> StaggeredGrid2D:
    """从 main.py 参数构建 staggered-grid。"""

    return StaggeredGrid2D(
        nx=int(params.forward.elastic2d_nx),
        nz=int(params.forward.elastic2d_nz),
        dx_m=float(params.forward.elastic2d_dx_m),
        dz_m=float(params.forward.elastic2d_dz_m),
    )
