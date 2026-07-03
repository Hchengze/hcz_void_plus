"""Rayleigh 波深度敏感性的简化近似。

真实 Rayleigh 波的深度敏感性与频率、层状介质、模态和材料参数有关。本模块
只提供一个科研原型阶段的低阶近似：用一个波长量级的穿透深度控制地下异常体
对地表响应的影响。它不是严格 Rayleigh 模态深度核。
"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np


def estimate_rayleigh_wavelength(rayleigh_velocity_mps: float, dominant_frequency_hz: float) -> float:
    """估计 Rayleigh 波主波长。

    物理意义：
        wavelength = velocity / dominant_frequency。这里的 dominant_frequency 来自
        统一参数中心，用于描述当前 Ricker 子波或主能量频带的量级。

    输出：
        波长，单位 m。
    """

    if rayleigh_velocity_mps <= 0:
        raise ValueError("rayleigh_velocity_mps 必须 > 0。")
    if dominant_frequency_hz <= 0:
        raise ValueError("dominant_frequency_hz 必须 > 0。")
    return rayleigh_velocity_mps / dominant_frequency_hz


def estimate_penetration_depth(params: SimpleNamespace) -> float:
    """估计 Rayleigh 波穿透深度。

    近似：
        penetration_depth = rayleigh_penetration_factor * wavelength。

    限制：
        这只是用于运动学地表响应示意和基础扫描加权的经验近似，不是严格模态
        计算结果。
    """

    return params.scan.rayleigh_penetration_factor * estimate_rayleigh_wavelength(
        params.velocity.rayleigh_velocity_mps,
        params.task.wavelet_dominant_frequency_hz,
    )


def rayleigh_depth_weight(depth_m: float | np.ndarray, penetration_depth_m: float) -> float | np.ndarray:
    """计算随深度指数衰减的简化 Rayleigh 敏感性权重。

    公式：
        weight = exp(-depth / penetration_depth)

    物理意义：
        Rayleigh 波能量主要集中在地表附近。浅部异常更容易影响地表响应，深部
        异常的影响应被抑制，避免在运动学扫描中对深部候选点过度乐观。
    """

    if penetration_depth_m <= 0:
        raise ValueError("penetration_depth_m 必须 > 0。")
    return np.exp(-np.asarray(depth_m, dtype=float) / penetration_depth_m)
