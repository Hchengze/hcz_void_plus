"""异常体对象和等效散射点生成。"""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import numpy as np


@dataclass(frozen=True)
class Anomaly:
    """浅层异常体的最小描述。

    物理意义：
        表示道路下方空洞、脱空或松散区等异常体的等效中心和尺度。

    输入参数单位：
        x0_m/y0_m/depth_m/radius_m 均为 m；scatter_strength 为无量纲相对强度。

    近似条件和限制：
        Stage 1 只将异常体转成等效散射点集合，不模拟真实空洞边界条件、
        弹性参数突变、模式转换或局部塌陷力学。
    """

    anomaly_type: str
    x0_m: float
    y0_m: float
    depth_m: float
    radius_m: float
    scatter_strength: float

    @property
    def center_xyz(self) -> np.ndarray:
        return np.array([self.x0_m, self.y0_m, self.depth_m], dtype=float)


def build_anomaly_from_params(params: SimpleNamespace) -> Anomaly:
    """从统一 params 构建异常体对象。"""

    return Anomaly(
        anomaly_type=params.anomaly.anomaly_type,
        x0_m=params.anomaly.x0_m,
        y0_m=params.anomaly.y0_m,
        depth_m=params.anomaly.depth_m,
        radius_m=params.anomaly.radius_m,
        scatter_strength=params.anomaly.scatter_strength,
    )


def anomaly_to_scatter_points(anomaly: Anomaly, mode: str) -> tuple[np.ndarray, np.ndarray]:
    """将异常体转换为等效散射点和权重。

    物理意义：
        当前正演采用运动学等效散射近似。一个 cavity 可以由中心散射点表示，
        也可以由中心点加若干边界点近似其空间尺度。

    输入参数：
        anomaly：异常体对象，坐标单位 m；
        mode：center 或 center_and_boundary。

    输出形状：
        scatter_xyz，shape = (n_scatter, 3)，单位 m；
        scatter_weight，shape = (n_scatter,)，无量纲。

    近似条件和限制：
        多个散射点表示异常体形状是允许保留的运动学近似，不是真实边界散射
        模拟；这些点只控制走时和相对振幅，不代表完整三维弹性波传播。
    """

    center = anomaly.center_xyz
    if mode == "center":
        points = center[None, :]
    elif mode == "center_and_boundary":
        r = anomaly.radius_m
        offsets = np.array(
            [
                [0.0, 0.0, 0.0],
                [r, 0.0, 0.0],
                [-r, 0.0, 0.0],
                [0.0, r, 0.0],
                [0.0, -r, 0.0],
                [0.0, 0.0, r],
                [0.0, 0.0, -0.5 * r],
            ],
            dtype=float,
        )
        points = center[None, :] + offsets
        points[:, 2] = np.maximum(points[:, 2], 0.05)
    else:
        raise ValueError(f"未知 scatter_point_mode={mode}，应为 center 或 center_and_boundary。")

    weights = np.full(points.shape[0], anomaly.scatter_strength / points.shape[0], dtype=float)
    return points, weights
