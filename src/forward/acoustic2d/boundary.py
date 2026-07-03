"""acoustic2d 简单 sponge 吸收边界。"""

from __future__ import annotations

import numpy as np


def build_sponge_damping(nz: int, nx: int, width: int = 12, strength: float = 0.015) -> np.ndarray:
    """构建二维 sponge 衰减系数。

    边界附近的 damping 小于 1，内部为 1。该实现很轻量，只用于原型验证，
    不是严格 PML。
    """

    damping = np.ones((nz, nx), dtype=float)
    for iz in range(nz):
        for ix in range(nx):
            distance_to_edge = min(iz, ix, nz - 1 - iz, nx - 1 - ix)
            if distance_to_edge < width:
                scale = (width - distance_to_edge) / max(width, 1)
                damping[iz, ix] = np.exp(-strength * scale * scale)
    return damping
