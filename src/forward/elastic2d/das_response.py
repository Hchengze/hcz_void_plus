"""从 elastic2d surface response 派生 DAS-like gauge strain。"""

from __future__ import annotations

import numpy as np


def compute_gauge_length_strain(
    surface_vx_gather: np.ndarray,
    dx_m: float,
    gauge_length_m: float,
) -> np.ndarray:
    """沿 receiver x 方向计算 gauge-length finite-difference strain。

    输入 surface_vx_gather 的 shape 为 time × receiver。当前假设光纤沿 x 方向，
    后续三维 receiver polyline 应沿局部切向方向计算。
    """

    gauge_samples = max(1, int(round(gauge_length_m / max(dx_m, 1.0e-9))))
    strain = np.zeros_like(surface_vx_gather, dtype=float)
    if surface_vx_gather.shape[1] <= gauge_samples:
        return strain
    numerator = surface_vx_gather[:, gauge_samples:] - surface_vx_gather[:, :-gauge_samples]
    strain[:, gauge_samples // 2 : gauge_samples // 2 + numerator.shape[1]] = numerator / (
        gauge_samples * dx_m
    )
    return strain


def accumulate_displacement_like(velocity_gather: np.ndarray, dt_s: float) -> np.ndarray:
    """由速度道积分得到 displacement-like 响应。

    当前 elastic2d prototype 直接输出 surface velocity。真实 DAS 与应变率/相位解调有关，
    本函数只为 Stage 5E 诊断提供 ux-like 累积量，帮助判断 gauge strain 为零到底来自
    物理响应弱，还是来自速度差分/接收点间距导致抵消。
    """

    return np.cumsum(np.asarray(velocity_gather, dtype=float), axis=0) * float(dt_s)


def compute_pairwise_gauge_strain(
    tangent_gather: np.ndarray,
    receiver_spacing_m: float,
    gauge_length_m: float,
) -> dict[str, np.ndarray | int | float]:
    """用非零偏移 receiver pair 计算 gauge strain。

    与 `compute_gauge_length_strain` 返回完整 gather 不同，这里显式返回 pair offset，
    便于报告检查 gauge_samples 是否过大、接收点数量是否不足，以及 strain 是否被
    差分配对抵消。
    """

    gather = np.asarray(tangent_gather, dtype=float)
    gauge_samples = max(1, int(round(gauge_length_m / max(receiver_spacing_m, 1.0e-9))))
    if gather.shape[1] <= gauge_samples:
        return {
            "strain": np.zeros_like(gather),
            "gauge_samples": gauge_samples,
            "pair_count": 0,
            "receiver_spacing_m": float(receiver_spacing_m),
        }
    pair_strain = (gather[:, gauge_samples:] - gather[:, :-gauge_samples]) / (
        gauge_samples * receiver_spacing_m
    )
    return {
        "strain": pair_strain,
        "gauge_samples": gauge_samples,
        "pair_count": int(pair_strain.shape[1]),
        "receiver_spacing_m": float(receiver_spacing_m),
    }


def build_elastic_das_response(
    surface_vx_gather: np.ndarray,
    surface_vz_gather: np.ndarray,
    dx_m: float,
    gauge_length_m: float,
) -> dict[str, np.ndarray]:
    """返回 point receiver 与 DAS-like strain 两种响应。

    point_receiver_gather 使用 surface vz，gauge_length_strain_gather 使用 surface vx 的
    gauge-length 差分。二者物理含义不同，不能在报告中混为一谈。
    """

    return {
        "point_vx_gather": np.asarray(surface_vx_gather, dtype=float),
        "point_receiver_gather": np.asarray(surface_vz_gather, dtype=float),
        "gauge_length_strain_gather": compute_gauge_length_strain(surface_vx_gather, dx_m, gauge_length_m),
    }
