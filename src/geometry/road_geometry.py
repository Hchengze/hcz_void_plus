"""道路几何辅助函数。"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np


def road_boundary_xy(params: SimpleNamespace) -> np.ndarray:
    """返回道路平面边界折线坐标。

    物理意义：
        道路区域在 x-y 平面内近似为矩形，x 沿道路方向，y 横穿道路方向。

    输入参数：
        params：main.py 解析后的参数对象。

    输出形状：
        boundary_xy，shape = (5, 2)，单位 m，首尾点闭合。

    近似条件和限制：
        仅用于几何 QC 绘图，不表达真实道路边界、路缘石或管线限制。
    """

    x0 = 0.0
    x1 = params.road.length_m
    y0 = 0.0
    y1 = params.road.width_m
    return np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]], dtype=float)
