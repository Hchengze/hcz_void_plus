"""分层等效 Rayleigh 速度模型。

道路近地表通常包含路面、基层、土体、回填区等结构。Stage 5A 不进入弹性波
全波场模拟，而是用“按深度查层速度 + 直线路径采样积分”的方式，把分层介质
引入运动学正演和定位走时。
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LayeredVelocityModel:
    """按深度 z 查询速度的分层等效 Rayleigh 模型。

    参数：
        layer_depths_m：每层底界深度，单位 m，向下为正，例如 [0.3, 1.0, 3.0, 8.0]。
        layer_rayleigh_velocities_mps：各层等效 Rayleigh 速度，单位 m/s，数量需与
            layer_depths_m 一致。
        reference_velocity_mps：代表性速度，用于旧接口、波长估计和图件标注。
    限制：
        速度只随 z 阶梯变化；走时积分仍沿直线段，不考虑 Snell 折射射线弯曲。
    """

    layer_depths_m: np.ndarray
    layer_rayleigh_velocities_mps: np.ndarray
    reference_velocity_mps: float
    model_type: str = "layered"

    def __post_init__(self) -> None:
        depths = np.asarray(self.layer_depths_m, dtype=float)
        velocities = np.asarray(self.layer_rayleigh_velocities_mps, dtype=float)
        if depths.ndim != 1 or velocities.ndim != 1:
            raise ValueError("layer depths 和 layer velocities 必须是一维数组。")
        if len(depths) != len(velocities):
            raise ValueError("layer_depths_m 与 layer_rayleigh_velocities_mps 数量必须一致。")
        if len(depths) < 1:
            raise ValueError("至少需要一层速度。")
        if np.any(depths <= 0.0) or np.any(np.diff(depths) <= 0.0):
            raise ValueError("layer_depths_m 必须为严格递增的正深度。")
        if np.any(velocities <= 0.0):
            raise ValueError("layer_rayleigh_velocities_mps 必须全部大于 0。")

    def get_velocity(self) -> float:
        """返回代表性速度。

        这里使用用户给定的 reference_velocity_mps，而不是简单平均层速度；
        这样可以保持 Rayleigh 波长估计与命令行主速度参数同步。
        """

        return float(self.reference_velocity_mps)

    def velocity_at(self, xyz: np.ndarray) -> np.ndarray:
        """返回任意三维点处的分层速度。

        xyz 的最后一维为 (x, y, z)。只有 z/depth 参与分层查表；x/y 在本模型中
        不改变速度。超过最后一个层底的点使用最后一层速度。
        """

        points = np.asarray(xyz, dtype=float)
        depth = np.maximum(points[..., 2], 0.0)
        layer_index = np.searchsorted(self.layer_depths_m, depth, side="left")
        layer_index = np.clip(layer_index, 0, len(self.layer_rayleigh_velocities_mps) - 1)
        return self.layer_rayleigh_velocities_mps[layer_index]
