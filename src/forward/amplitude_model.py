"""layered_kinematic 正演振幅模型。

Stage 5J 将 direct/scatter 的振幅从单纯几何扩散推进到
``geometric * Q attenuation * depth decay`` 的轻量经验模型。
该模型服务三维道路 DAS-like 运动学正演，不是粘弹性波动方程。
"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from src.model.attenuation_model import AttenuationModel, build_attenuation_model


def _path_length(start_xyz: np.ndarray, end_xyz: np.ndarray) -> np.ndarray:
    """计算广播后的三维直线路径长度。"""

    start, end = np.broadcast_arrays(np.asarray(start_xyz, dtype=float), np.asarray(end_xyz, dtype=float))
    return np.linalg.norm(end - start, axis=-1)


def geometric_spreading(path_m: np.ndarray | float, attenuation: AttenuationModel) -> np.ndarray:
    """计算 1/(path+1)^p 几何扩散项。"""

    path = np.asarray(path_m, dtype=float)
    return 1.0 / np.power(np.maximum(path, 0.0) + 1.0, attenuation.geometric_spreading_power)


def compute_direct_amplitude(
    params: SimpleNamespace,
    start_xyz: np.ndarray,
    end_xyz: np.ndarray,
    travel_time_s: np.ndarray | float,
    attenuation: AttenuationModel | None = None,
) -> np.ndarray:
    """计算 direct arrival 的路径相关振幅。

    direct 振幅包含几何扩散和 Q attenuation，不包含异常体深度权重。
    """

    attenuation = attenuation or build_attenuation_model(params)
    path = _path_length(start_xyz, end_xyz)
    q_eff = attenuation.effective_q_for_path(start_xyz, end_xyz)
    amp = geometric_spreading(path, attenuation)
    amp *= attenuation.q_decay(travel_time_s, params.task.wavelet_dominant_frequency_hz, q_eff)
    return np.maximum(amp, attenuation.min_amplitude if attenuation.enabled else 0.0)


def compute_scatter_amplitude(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    travel_time_s: np.ndarray | float,
    scatter_weight: np.ndarray | float,
    attenuation: AttenuationModel | None = None,
) -> np.ndarray:
    """计算 source-scatter-receiver 的等效散射振幅。

    scatter 振幅包含：
    1. 异常体散射权重；
    2. source-scatter 与 scatter-receiver 总路径几何扩散；
    3. 两段路径的等效 Q attenuation；
    4. Rayleigh 深度敏感性近似 exp(-h / penetration_depth)。
    """

    attenuation = attenuation or build_attenuation_model(params)
    source = np.asarray(source_xyz, dtype=float)
    scatter = np.asarray(scatter_xyz, dtype=float)
    receiver = np.asarray(receiver_xyz, dtype=float)
    source_path = _path_length(source, scatter)
    receiver_path = _path_length(scatter, receiver)
    total_path = source_path + receiver_path
    q_source = attenuation.effective_q_for_path(source, scatter)
    q_receiver = attenuation.effective_q_for_path(scatter, receiver)
    q_eff = 2.0 / (1.0 / np.maximum(q_source, 1.0e-6) + 1.0 / np.maximum(q_receiver, 1.0e-6))
    depth = np.asarray(scatter[..., 2], dtype=float)
    depth_decay = np.exp(-np.maximum(depth, 0.0) / max(params.derived.rayleigh_penetration_depth_m, 1.0e-6))
    amp = np.asarray(scatter_weight, dtype=float) * geometric_spreading(total_path, attenuation)
    amp *= attenuation.q_decay(travel_time_s, params.task.wavelet_dominant_frequency_hz, q_eff)
    amp *= depth_decay
    if not attenuation.enabled:
        return amp
    # 散射权重未来可能带符号；幅值下限只保护数值量级，不能把负散射事件强行翻成正号。
    sign = np.where(amp < 0.0, -1.0, 1.0)
    return sign * np.maximum(np.abs(amp), attenuation.min_amplitude)


def attenuation_comparison_summary(attenuated: np.ndarray, reference: np.ndarray) -> dict[str, float | bool]:
    """比较启用 attenuation 前后的炮集 RMS 差异。"""

    a = np.asarray(attenuated, dtype=float)
    b = np.asarray(reference, dtype=float)
    diff = a - b
    reference_rms = float(np.sqrt(np.mean(b * b)))
    diff_rms = float(np.sqrt(np.mean(diff * diff)))
    return {
        "attenuation_comparison_available": True,
        "attenuated_rms": float(np.sqrt(np.mean(a * a))),
        "reference_no_attenuation_rms": reference_rms,
        "rms_difference": diff_rms,
        "relative_rms_difference": float(diff_rms / max(reference_rms, 1.0e-12)),
    }
