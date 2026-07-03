"""扫描网格构建。"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np


def build_scan_grid(params: SimpleNamespace) -> dict[str, np.ndarray | tuple[int, int, int] | int]:
    """从 main.py 派生参数构建 x-y-h 扫描网格。

    输出：
        x_grid、y_grid、depth_grid、shape、point_count。

    说明：
        网格本身已经由 main.py 统一派生和校验；这里不重新定义范围或步长，只
        把 params.derived 中的数组组织成扫描模块需要的形式。
    """

    return {
        "x_grid": params.derived.scan_x_grid,
        "y_grid": params.derived.scan_y_grid,
        "depth_grid": params.derived.scan_depth_grid,
        "shape": params.derived.scan_shape,
        "point_count": params.derived.scan_grid_point_count,
    }
