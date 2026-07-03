"""Rayleigh 等效速度诊断工具。

本模块不做严格 Rayleigh 模态求解，只提供 Stage 5A 报告和验证实验需要的
等效速度、层状速度曲线和路径平均速度辅助函数。
"""

from __future__ import annotations

import numpy as np

from src.model.velocity_model import KinematicVelocityModel, compute_effective_velocity_for_path


def sample_velocity_profile(
    velocity_model: KinematicVelocityModel,
    max_depth_m: float,
    n_samples: int = 120,
) -> dict[str, np.ndarray]:
    """采样 z 方向速度剖面。

    输出用于 `fig_layered_velocity_profile.png`。x/y 固定为 0，z 从 0 到
    max_depth_m，展示当前模型的近地表等效 Rayleigh 速度随深度变化。
    """

    depth = np.linspace(0.0, max_depth_m, n_samples, dtype=float)
    xyz = np.column_stack([np.zeros_like(depth), np.zeros_like(depth), depth])
    velocity = velocity_model.velocity_at(xyz)
    return {"depth_m": depth, "velocity_mps": np.asarray(velocity, dtype=float)}


def compare_path_effective_velocity(
    start_xyz: np.ndarray,
    end_xyz: np.ndarray,
    velocity_model: KinematicVelocityModel,
) -> dict[str, float]:
    """计算一条路径的长度、走时和等效速度。"""

    start = np.asarray(start_xyz, dtype=float)
    end = np.asarray(end_xyz, dtype=float)
    length = float(np.linalg.norm(end - start))
    effective_velocity = float(compute_effective_velocity_for_path(start, end, velocity_model))
    travel_time = length / max(effective_velocity, 1.0e-12)
    return {
        "path_length_m": length,
        "travel_time_s": travel_time,
        "effective_velocity_mps": effective_velocity,
    }
