"""震源三维点集生成。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np


def _read_xyz_csv(path: str | Path) -> np.ndarray:
    """读取包含 x_m,y_m,z_m 列的震源 CSV。"""

    table = np.genfromtxt(path, delimiter=",", names=True, dtype=float, encoding="utf-8")
    if table.size == 0:
        raise ValueError(f"CSV 为空：{path}")
    names = set(table.dtype.names or [])
    required = {"x_m", "y_m", "z_m"}
    if not required.issubset(names):
        raise ValueError(f"source CSV 必须包含列 {sorted(required)}，当前列为 {sorted(names)}。")
    return np.column_stack([np.atleast_1d(table["x_m"]), np.atleast_1d(table["y_m"]), np.atleast_1d(table["z_m"])])


def _build_source_grid(params: SimpleNamespace) -> np.ndarray:
    """用现有 shot_count 生成轻量二维震源网格。

    由于 Stage 4A 不新增复杂 survey 设计参数，这里用 shot_count 自动填充一个
    x-y 网格：x 方向沿 source_x_start/spacing 展开，y 方向在道路两侧范围内取两行。
    该模式主要用于验证三维 source_xyz 管线，后续可扩展为任意 survey 文件。
    """

    n_shot = params.source.shot_count
    n_y = 2 if n_shot > 1 else 1
    n_x = int(np.ceil(n_shot / n_y))
    x_values = params.source.x_start_m + np.arange(n_x, dtype=float) * params.source.shot_spacing_m
    y_values = np.linspace(params.fiber.y_m, params.source.y_m, n_y)
    points = []
    for y_m in y_values:
        for x_m in x_values:
            points.append([x_m, y_m, params.source.z_m])
            if len(points) == n_shot:
                return np.array(points, dtype=float)
    return np.array(points[:n_shot], dtype=float)


def build_source_xyz(params: SimpleNamespace) -> np.ndarray:
    """根据 params 构建任意三维震源点集。"""

    if params.source.geometry_mode == "csv":
        source_xyz = _read_xyz_csv(params.source.points_csv)
    elif params.source.geometry_mode == "grid":
        source_xyz = _build_source_grid(params)
    else:
        source_xyz = np.column_stack(
            [
                params.derived.shot_x,
                np.full(params.source.shot_count, params.source.y_m),
                np.full(params.source.shot_count, params.source.z_m),
            ]
        )
    if source_xyz.ndim != 2 or source_xyz.shape[1] != 3:
        raise ValueError(f"source_xyz shape 错误：{source_xyz.shape}，应为 (n_source, 3)。")
    return source_xyz.astype(float)

