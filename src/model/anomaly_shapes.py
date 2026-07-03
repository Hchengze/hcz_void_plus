"""三维异常体等效散射点形状生成。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class AnomalyShapeSpec:
    """三维异常体形状参数。

    所有尺寸单位为 m，orientation_deg 为 x-y 平面内绕 z 轴旋转角。该对象只用于
    生成运动学等效散射点，不代表真实空洞边界条件或弹性参数分布。
    """

    shape: str
    size_x_m: float
    size_y_m: float
    size_z_m: float
    orientation_deg: float
    density: str


def _rotate_xy(offsets: np.ndarray, orientation_deg: float) -> np.ndarray:
    """在 x-y 平面旋转散射点偏移。"""

    angle = np.deg2rad(orientation_deg)
    rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]], dtype=float)
    rotated = offsets.copy()
    rotated[:, :2] = offsets[:, :2] @ rotation.T
    return rotated


def _base_offsets(spec: AnomalyShapeSpec) -> np.ndarray:
    """生成未旋转的三维形状偏移点。"""

    hx = 0.5 * spec.size_x_m
    hy = 0.5 * spec.size_y_m
    hz = 0.5 * spec.size_z_m
    if spec.density == "center":
        return np.array([[0.0, 0.0, 0.0]], dtype=float)
    if spec.shape == "sphere":
        r = max(spec.size_x_m, spec.size_y_m, spec.size_z_m) * 0.5
        offsets = [[0, 0, 0], [r, 0, 0], [-r, 0, 0], [0, r, 0], [0, -r, 0], [0, 0, hz], [0, 0, -hz]]
    elif spec.shape == "ellipsoid":
        offsets = [[0, 0, 0], [hx, 0, 0], [-hx, 0, 0], [0, hy, 0], [0, -hy, 0], [0, 0, hz], [0, 0, -hz]]
    elif spec.shape == "box":
        offsets = [[sx * hx, sy * hy, sz * hz] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
        offsets.append([0, 0, 0])
    elif spec.shape in {"cylinder", "pipe_trench"}:
        # 长条形目标默认沿 x 方向展开，pipe_trench 表示管沟/管线扰动带，可用更长的 x 尺度。
        n_axis = 5 if spec.density == "medium" else 3
        x_values = np.linspace(-hx, hx, n_axis)
        offsets = [[x, 0, 0] for x in x_values]
        offsets += [[x, hy, 0] for x in x_values] + [[x, -hy, 0] for x in x_values]
        offsets += [[x, 0, hz] for x in x_values] + [[x, 0, -hz] for x in x_values]
    else:
        raise ValueError(f"未知 anomaly_shape={spec.shape}")
    offsets = np.array(offsets, dtype=float)
    if spec.density == "medium" and spec.shape not in {"cylinder", "pipe_trench"}:
        extra = 0.5 * offsets
        offsets = np.vstack([offsets, extra])
    return offsets


def generate_shape_scatter_points(center_xyz: np.ndarray, spec: AnomalyShapeSpec) -> np.ndarray:
    """根据三维异常体形状生成等效散射点。

    输出：
        scatter_xyz，shape = (n_scatter, 3)，单位 m。

    限制：
        这些点只是 equivalent scatter representation，用于运动学走时和相对振幅。
        它们不是真实边界散射点，不包含模式转换、空洞边界条件或弹性全波场效应。
    """

    offsets = _rotate_xy(_base_offsets(spec), spec.orientation_deg)
    points = center_xyz[None, :] + offsets
    points[:, 2] = np.maximum(points[:, 2], 0.05)
    return points

