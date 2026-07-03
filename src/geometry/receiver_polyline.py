"""DAS-like 接收点三维 polyline 生成。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np


def _read_xyz_csv(path: str | Path) -> np.ndarray:
    """读取包含 x_m,y_m,z_m 列的 CSV 文件。

    限制：
        本函数只读取明确列名的轻量 CSV，不做复杂坐标投影、里程转换或工程测量
        坐标系统处理。CSV 中的坐标必须已经是项目统一的 x-y-z，单位 m。
    """

    table = np.genfromtxt(path, delimiter=",", names=True, dtype=float, encoding="utf-8")
    if table.size == 0:
        raise ValueError(f"CSV 为空：{path}")
    names = set(table.dtype.names or [])
    required = {"x_m", "y_m", "z_m"}
    if not required.issubset(names):
        raise ValueError(f"receiver CSV 必须包含列 {sorted(required)}，当前列为 {sorted(names)}。")
    return np.column_stack([np.atleast_1d(table["x_m"]), np.atleast_1d(table["y_m"]), np.atleast_1d(table["z_m"])])


def build_receiver_xyz(params: SimpleNamespace) -> np.ndarray:
    """根据 params 构建任意三维接收点集。

    straight：
        使用 channel_x + fiber_y + fiber_z/burial_depth 生成默认直线光纤。
    polyline_csv：
        从 CSV 读取三维接收点。后续正演、扫描和可视化只使用 receiver_xyz，不再
        假设接收点一定在直线上。
    """

    if params.fiber.geometry_mode == "polyline_csv":
        receiver_xyz = _read_xyz_csv(params.fiber.polyline_csv)
    else:
        receiver_xyz = np.column_stack(
            [
                params.derived.channel_x,
                np.full(params.fiber.channel_count, params.fiber.y_m),
                np.full(params.fiber.channel_count, params.fiber.z_m),
            ]
        )
    if receiver_xyz.ndim != 2 or receiver_xyz.shape[1] != 3:
        raise ValueError(f"receiver_xyz shape 错误：{receiver_xyz.shape}，应为 (n_receiver, 3)。")
    return receiver_xyz.astype(float)

