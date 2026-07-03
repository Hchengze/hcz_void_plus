"""横向非均匀与局部低速等效 Rayleigh 速度模型。

这些模型用于 Stage 5A 的近地表运动学实验：它们可以表达道路横向渐变、
回填区或异常体附近低速扰动，但仍通过 straight-ray kinematic approximation
计算走时，不代表真实三维弹性波场。
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.model.velocity_model import KinematicVelocityModel


@dataclass(frozen=True)
class LateralGradientVelocityModel:
    """随 x/y 线性变化的等效速度模型。

    物理用途：
        用于模拟道路横向回填差异、路基材料变化或施工扰动导致的缓慢速度变化。
    限制：
        这是局部线性近似；不会自动保证复杂地质边界，也不做射线弯曲。
    """

    reference_velocity_mps: float
    gradient_x_mps_per_m: float = 0.0
    gradient_y_mps_per_m: float = 0.0
    reference_x_m: float = 0.0
    reference_y_m: float = 0.0
    min_velocity_mps: float = 50.0
    model_type: str = "lateral_gradient"

    def get_velocity(self) -> float:
        return float(self.reference_velocity_mps)

    def velocity_at(self, xyz: np.ndarray) -> np.ndarray:
        points = np.asarray(xyz, dtype=float)
        velocity = (
            self.reference_velocity_mps
            + self.gradient_x_mps_per_m * (points[..., 0] - self.reference_x_m)
            + self.gradient_y_mps_per_m * (points[..., 1] - self.reference_y_m)
        )
        return np.maximum(velocity, self.min_velocity_mps)


@dataclass(frozen=True)
class LocalizedLowVelocityZoneModel:
    """局部低速区速度模型。

    物理用途：
        用于近似管沟回填区、松散区、含水扰动或异常体附近低速扰动对走时的影响。
        低速区通过中心、半径和速度折减因子表达。
    限制：
        低速区是平滑权重扰动，不是真实弹性参数反演；不会产生散射、反射或模式转换，
        只改变运动学走时积分中的局部速度。
    """

    base_model: KinematicVelocityModel
    center_xyz_m: np.ndarray
    radius_m: float
    low_velocity_factor: float
    enabled: bool = True
    model_type: str = "localized_low_velocity_zone"

    def get_velocity(self) -> float:
        return float(self.base_model.get_velocity())

    def velocity_at(self, xyz: np.ndarray) -> np.ndarray:
        points = np.asarray(xyz, dtype=float)
        base_velocity = np.asarray(self.base_model.velocity_at(points), dtype=float)
        if not self.enabled:
            return base_velocity
        center = np.asarray(self.center_xyz_m, dtype=float)
        distance = np.linalg.norm(points - center, axis=-1)
        # 使用高斯型平滑扰动，避免速度在低速区边界突变。半径越小，扰动越局部。
        weight = np.exp(-0.5 * (distance / max(self.radius_m, 1.0e-6)) ** 2)
        factor = 1.0 - (1.0 - self.low_velocity_factor) * weight
        return np.maximum(base_velocity * factor, 50.0)
