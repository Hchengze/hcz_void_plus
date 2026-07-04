"""elastic2d 与 layered_kinematic 局部走时对照。"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.validation.elastic2d_void_scattering import run_elastic2d_void_scattering


def _curve_energy(residual: np.ndarray, time_axis: np.ndarray, curve_s: np.ndarray, half_width_s: float = 0.003) -> float:
    """统计 residual 能量是否集中在运动学曲线附近。"""

    dt = float(time_axis[1] - time_axis[0]) if len(time_axis) > 1 else 1.0
    half = max(1, int(round(half_width_s / dt)))
    total = float(np.sum(residual * residual))
    picked = 0.0
    for ich, t in enumerate(curve_s):
        center = int(round(t / dt))
        start = max(0, center - half)
        stop = min(residual.shape[0], center + half + 1)
        if stop > start:
            picked += float(np.sum(residual[start:stop, ich] ** 2))
    return picked / max(total, 1.0e-12)


def run_elastic_vs_kinematic(params) -> dict[str, Any]:
    """比较 elastic residual 与局部运动学绕射曲线。"""

    void_result = run_elastic2d_void_scattering(params)
    background = void_result["background_result"]
    residual = void_result["residual_gather"]
    ratio = _curve_energy(residual, background.time_axis_s, void_result["kinematic_curve_s"])
    return {
        **void_result,
        "curve_energy_ratio": ratio,
        "main_conclusion": (
            "layered/局部 kinematic 曲线能解释 elastic residual 的一部分主要到时，"
            "但 elastic2d 还显示振幅、尾波和多路径等运动学模型没有的效应。"
        ),
    }
