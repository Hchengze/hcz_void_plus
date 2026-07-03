"""acoustic2d 原型网格与介质构建。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Acoustic2DGrid:
    """二维声学网格。

    x 为水平距离，z 为深度，均匀网格。当前 constant density，只传播标量声压场。
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


def build_layered_acoustic_velocity(grid: Acoustic2DGrid, layer_depths_m: list[float], velocities_mps: list[float]) -> np.ndarray:
    """生成简单分层 acoustic velocity。

    该速度场仅用于 acoustic2d prototype 的数值框架验证，不等同于 Rayleigh 波速度。
    """

    z = grid.z_m[:, None]
    velocity = np.empty((grid.nz, grid.nx), dtype=float)
    depths = np.asarray(layer_depths_m, dtype=float)
    values = np.asarray(velocities_mps, dtype=float)
    layer_index = np.searchsorted(depths, z[:, 0], side="left")
    layer_index = np.clip(layer_index, 0, len(values) - 1)
    velocity[:, :] = values[layer_index, None]
    return velocity
