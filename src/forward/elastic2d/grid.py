"""elastic2d 最小原型网格。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Elastic2DGrid:
    """二维 x-z 均匀网格。

    本原型采用 collocated-grid，把 vx、vz、sxx、szz、sxz 放在同一网格点上。
    这种做法便于审计和测试，但数值色散、自由表面精度和稳定性不如严格 staggered-grid。
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
