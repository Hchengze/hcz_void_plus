"""近地表等效 Rayleigh 速度模型统一入口。

本文件是 Stage 5A 的速度模型总接口。项目仍然坚持 kinematic approximation：
走时通过 source_xyz / receiver_xyz / candidate_xyz 之间的直线路径采样积分获得，
不是 Snell 射线追踪，更不是三维弹性波方程数值模拟。这样做的目的，是在不进入
elastic3d/FEM/FWI 的前提下，把“均匀等效速度”推进到更接近道路近地表的分层与
横向非均匀等效 Rayleigh 速度表达。
"""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Protocol

import numpy as np


class KinematicVelocityModel(Protocol):
    """所有运动学速度模型需要满足的最小接口。"""

    model_type: str

    def velocity_at(self, xyz: np.ndarray) -> np.ndarray:
        """返回点位置处的局部等效 Rayleigh 速度，单位 m/s。"""

    def get_velocity(self) -> float:
        """返回一个代表性速度，供旧接口、图件尺度和 Rayleigh 波长估计使用。"""


@dataclass(frozen=True)
class UniformVelocityModel:
    """均匀等效 Rayleigh 速度模型。

    物理意义：
        用单一等效 Rayleigh 速度代表道路浅层介质。该模型便于基准对比，
        但会忽略路面结构层、回填区、局部低速带和横向变化。
    限制：
        仅适合做 Stage 5A 的基线模型，不应再被描述为唯一可用速度模型。
    """

    rayleigh_velocity_mps: float
    model_type: str = "uniform"

    def get_velocity(self) -> float:
        return float(self.rayleigh_velocity_mps)

    def velocity_at(self, xyz: np.ndarray) -> np.ndarray:
        points = np.asarray(xyz, dtype=float)
        shape = points.shape[:-1] if points.ndim > 1 else ()
        return np.full(shape, self.rayleigh_velocity_mps, dtype=float)


def _parse_float_list(value: str | list[float] | tuple[float, ...]) -> list[float]:
    """解析 main.py 传入的逗号分隔浮点列表。"""

    if isinstance(value, (list, tuple)):
        return [float(item) for item in value]
    return [float(item.strip()) for item in str(value).split(",") if item.strip()]


def compute_kinematic_travel_time(
    start_xyz: np.ndarray,
    end_xyz: np.ndarray,
    velocity_model: KinematicVelocityModel,
    n_samples: int = 24,
) -> np.ndarray:
    """计算直线路径采样积分走时。

    输入：
        start_xyz：shape 可为 (3,) 或 (N, 3)，单位 m。
        end_xyz：shape 可为 (3,) 或 (N, 3)，单位 m。
        velocity_model：支持 velocity_at(xyz) 的速度模型对象。
        n_samples：路径采样点数。采样越密，分层/非均匀积分越平滑。
    输出：
        travel_time：按广播后的路径数量返回，单位 s。
    近似条件：
        路径仍按直线段处理，不做射线弯曲；分层/非均匀只通过 ds/v(x,y,z)
        积分进入走时。这是 straight-ray kinematic approximation。
    """

    if not hasattr(velocity_model, "velocity_at"):
        velocity_model = UniformVelocityModel(float(velocity_model))

    start = np.asarray(start_xyz, dtype=float)
    end = np.asarray(end_xyz, dtype=float)
    start_b, end_b = np.broadcast_arrays(start, end)
    segment = end_b - start_b
    length = np.linalg.norm(segment, axis=-1)
    if np.all(length == 0.0):
        return np.zeros_like(length, dtype=float)

    fractions = np.linspace(0.0, 1.0, max(2, int(n_samples)), dtype=float)
    fraction_shape = (1,) * (start_b.ndim - 1) + (len(fractions), 1)
    sample_xyz = start_b[..., None, :] + fractions.reshape(fraction_shape) * segment[..., None, :]
    # 对每条直线路径采样局部速度，用调和平均思想积分 ds/v。
    local_velocity = np.maximum(velocity_model.velocity_at(sample_xyz), 1.0e-6)
    slowness_mean = np.mean(1.0 / local_velocity, axis=-1)
    return length * slowness_mean


def compute_effective_velocity_for_path(
    start_xyz: np.ndarray,
    end_xyz: np.ndarray,
    velocity_model: KinematicVelocityModel,
    n_samples: int = 24,
) -> np.ndarray:
    """返回直线路径的等效速度。

    该速度定义为路径长度除以积分走时，主要用于 metadata、诊断图和测试。
    它不是 Rayleigh 模态相速度反演结果。
    """

    start = np.asarray(start_xyz, dtype=float)
    end = np.asarray(end_xyz, dtype=float)
    length = np.linalg.norm(np.asarray(end) - np.asarray(start), axis=-1)
    time = compute_kinematic_travel_time(start, end, velocity_model, n_samples=n_samples)
    return length / np.maximum(time, 1.0e-12)


def compute_scatter_travel_time(
    source_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    velocity_model: KinematicVelocityModel,
    n_samples: int = 24,
) -> np.ndarray:
    """计算 source -> scatter -> receiver 的三维运动学散射走时。

    输入形状：
        source_xyz：shape = (n_shot, 3)
        scatter_xyz：shape = (n_scatter, 3) 或 (3,)
        receiver_xyz：shape = (n_channel, 3)
    输出形状：
        travel_time：shape = (n_shot, n_scatter, n_channel)，单位 s。
    物理意义：
        用候选异常体等效散射点构造绕射/散射走时曲面。异常体深度作为 z 坐标
        参与三维路径积分，但当前仍不是边界散射或模式转换模拟。
    """

    source = np.asarray(source_xyz, dtype=float)
    scatter = np.asarray(scatter_xyz, dtype=float).reshape(-1, 3)
    receiver = np.asarray(receiver_xyz, dtype=float)
    t_source_scatter = compute_kinematic_travel_time(
        source[:, None, :],
        scatter[None, :, :],
        velocity_model,
        n_samples=n_samples,
    )
    t_scatter_receiver = compute_kinematic_travel_time(
        scatter[:, None, :],
        receiver[None, :, :],
        velocity_model,
        n_samples=n_samples,
    )
    return t_source_scatter[:, :, None] + t_scatter_receiver[None, :, :]


def build_velocity_model(params: SimpleNamespace) -> KinematicVelocityModel:
    """从统一 params 构建速度模型。

    所有速度参数都来自 main.py 的 argparse 和派生校验结果；算法模块不得私自维护
    第二套速度参数。Stage 5A 默认使用 layered，但仍保留 uniform 作为基线。
    """

    model_type = params.velocity.model_type
    if model_type == "uniform":
        return UniformVelocityModel(params.velocity.rayleigh_velocity_mps)

    if model_type in {"layered", "layered_with_anomaly_perturbation"}:
        from src.model.layered_velocity import LayeredVelocityModel

        base_model = LayeredVelocityModel(
            layer_depths_m=np.asarray(params.velocity.layer_depths_m, dtype=float),
            layer_rayleigh_velocities_mps=np.asarray(params.velocity.layer_rayleigh_velocities_mps, dtype=float),
            reference_velocity_mps=params.velocity.rayleigh_velocity_mps,
            model_type=model_type,
        )
        if model_type == "layered":
            return base_model

        from src.model.heterogeneous_velocity import LocalizedLowVelocityZoneModel

        return LocalizedLowVelocityZoneModel(
            base_model=base_model,
            center_xyz_m=np.asarray(
                [
                    params.velocity.low_velocity_zone_x0_m,
                    params.velocity.low_velocity_zone_y0_m,
                    params.velocity.low_velocity_zone_depth_m,
                ],
                dtype=float,
            ),
            radius_m=params.velocity.low_velocity_zone_radius_m,
            low_velocity_factor=params.velocity.low_velocity_factor,
            enabled=True,
            model_type=model_type,
        )

    if model_type == "lateral_gradient":
        from src.model.heterogeneous_velocity import LateralGradientVelocityModel

        return LateralGradientVelocityModel(
            reference_velocity_mps=params.velocity.rayleigh_velocity_mps,
            gradient_x_mps_per_m=params.velocity.lateral_gradient_x_mps_per_m,
            gradient_y_mps_per_m=params.velocity.lateral_gradient_y_mps_per_m,
        )

    if model_type == "localized_low_velocity_zone":
        from src.model.heterogeneous_velocity import LocalizedLowVelocityZoneModel

        return LocalizedLowVelocityZoneModel(
            base_model=UniformVelocityModel(params.velocity.rayleigh_velocity_mps),
            center_xyz_m=np.asarray(
                [
                    params.velocity.low_velocity_zone_x0_m,
                    params.velocity.low_velocity_zone_y0_m,
                    params.velocity.low_velocity_zone_depth_m,
                ],
                dtype=float,
            ),
            radius_m=params.velocity.low_velocity_zone_radius_m,
            low_velocity_factor=params.velocity.low_velocity_factor,
            enabled=params.velocity.low_velocity_zone_enabled,
            model_type=model_type,
        )

    raise ValueError(f"不支持的 velocity_model_type：{model_type}")
