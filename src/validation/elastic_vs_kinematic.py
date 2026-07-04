"""elastic2d 与 layered_kinematic 局部走时对照。

本模块检查 elastic2d residual 是否集中在局部 kinematic diffraction curve 附近。
它不把 2D elastic 当成三维主定位流程，而是用局部物理验证来判断当前 kinematic
score 的可解释边界。
"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.validation.elastic2d_void_scattering import run_elastic2d_void_scattering


def _curve_energy_components(
    residual: np.ndarray,
    time_axis: np.ndarray,
    curve_s: np.ndarray,
    half_width_s: float = 0.003,
    time_shift_s: float = 0.0,
) -> tuple[float, float]:
    """返回曲线附近与曲线外 residual 能量。"""

    dt = float(time_axis[1] - time_axis[0]) if len(time_axis) > 1 else 1.0
    half = max(1, int(round(half_width_s / dt)))
    mask = np.zeros_like(residual, dtype=bool)
    for ich, t in enumerate(curve_s + time_shift_s):
        center = int(round(t / dt))
        start = max(0, center - half)
        stop = min(residual.shape[0], center + half + 1)
        if stop > start:
            mask[start:stop, ich] = True
    near = float(np.sum(residual[mask] ** 2))
    total = float(np.sum(residual * residual))
    return near, max(total - near, 0.0)


def _best_time_shift(
    residual: np.ndarray,
    time_axis: np.ndarray,
    curve_s: np.ndarray,
    half_width_s: float = 0.003,
) -> dict[str, float]:
    """在 ±10 ms 内搜索使曲线窗能量最大的整体时间平移。"""

    shifts = np.linspace(-0.01, 0.01, 21)
    total = float(np.sum(residual * residual))
    best_shift = 0.0
    best_near = -1.0
    for shift in shifts:
        near, _ = _curve_energy_components(residual, time_axis, curve_s, half_width_s, float(shift))
        if near > best_near:
            best_near = near
            best_shift = float(shift)
    return {
        "best_time_shift_ms": 1000.0 * best_shift,
        "best_shift_near_energy": best_near,
        "best_shift_explained_fraction": best_near / max(total, 1.0e-12),
    }


def run_elastic_vs_kinematic(params) -> dict[str, Any]:
    """比较 elastic residual 与局部运动学绕射曲线。"""

    void_result = run_elastic2d_void_scattering(params)
    background = void_result["background_result"]
    residual = void_result["residual_gather"]
    curve_s = void_result["kinematic_curve_s"]
    near, off = _curve_energy_components(residual, background.time_axis_s, curve_s)
    total = near + off
    shift = _best_time_shift(residual, background.time_axis_s, curve_s)
    explained = near / max(total, 1.0e-12)
    extra = off / max(total, 1.0e-12)
    return {
        **void_result,
        "curve_energy_ratio": explained,
        "residual_energy_near_kinematic_curve_ratio": explained,
        "residual_energy_off_curve_ratio": extra,
        "best_time_shift_ms": shift["best_time_shift_ms"],
        "kinematic_curve_explained_fraction": shift["best_shift_explained_fraction"],
        "elastic_extra_event_fraction": 1.0 - shift["best_shift_explained_fraction"],
        "main_conclusion": (
            "layered/局部 kinematic 曲线只能解释 elastic residual 的一部分能量；"
            "曲线外 residual 代表振幅、尾波、多路径、边界和弹性模式等运动学模型没有的效应。"
        ),
    }
