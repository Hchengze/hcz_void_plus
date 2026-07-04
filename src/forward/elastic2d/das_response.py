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
        "point_receiver_gather": np.asarray(surface_vz_gather, dtype=float),
        "gauge_length_strain_gather": compute_gauge_length_strain(surface_vx_gather, dx_m, gauge_length_m),
    }
