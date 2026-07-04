"""elastic2d 边界阻尼。"""

from __future__ import annotations

import numpy as np


def build_elastic_sponge(nz: int, nx: int, thickness: int = 12, strength: float = 0.015) -> np.ndarray:
    """构建简单 sponge absorbing boundary。

    顶部需要近似自由表面，因此这里不在 z=0 顶部施加强阻尼，只对左右和底部加强
    衰减。该 sponge 不是严格 PML。
    """

    damping = np.ones((nz, nx), dtype=float)
    for ix in range(nx):
        left = max(0, thickness - ix)
        right = max(0, ix - (nx - thickness - 1))
        distance = max(left, right)
        if distance > 0:
            damping[:, ix] *= np.exp(-strength * distance**2)
    for iz in range(nz):
        bottom = max(0, iz - (nz - thickness - 1))
        if bottom > 0:
            damping[iz, :] *= np.exp(-strength * bottom**2)
    return damping
