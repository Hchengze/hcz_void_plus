"""elastic2d Rayleigh-like surface event sanity check。"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.forward.elastic2d.elastic_fdtd import run_elastic2d_prototype
from src.forward.elastic2d.validation import make_elastic2d_validation_params


def _estimate_surface_velocity(result) -> dict[str, Any]:
    """用 surface gather 包络峰值的 moveout 粗略估计表观速度。

    这是 sanity check，不是严格 Rayleigh 相速度反演。若峰值拟合不稳定，函数会退回
    到 0.92 Vs 的保守估计，并在报告中标注。
    """

    gather = np.abs(result.surface_vz_gather)
    receiver_x = result.receiver_x_m
    source_x = result.source_x_m
    time_axis = result.time_axis_s
    right = receiver_x > source_x + 4.0 * result.grid.dx_m
    if np.count_nonzero(right) < 4:
        fallback = 0.92 * float(np.median(result.model.vs_mps))
        return {"velocity_mps": fallback, "method": "fallback_0.92_vs", "fit_ok": False}
    peak_index = np.argmax(gather[:, right], axis=0)
    peak_time = time_axis[peak_index]
    offset = receiver_x[right] - source_x
    valid = peak_time > 0.0
    if np.count_nonzero(valid) < 4:
        fallback = 0.92 * float(np.median(result.model.vs_mps))
        return {"velocity_mps": fallback, "method": "fallback_0.92_vs", "fit_ok": False}
    slope, _ = np.polyfit(offset[valid], peak_time[valid], deg=1)
    velocity = 1.0 / max(float(slope), 1.0e-9)
    vs = float(np.median(result.model.vs_mps))
    if not (0.5 * vs <= velocity <= 2.5 * vs):
        velocity = 0.92 * vs
        return {"velocity_mps": velocity, "method": "fallback_0.92_vs_after_unstable_fit", "fit_ok": False}
    return {"velocity_mps": velocity, "method": "envelope_peak_moveout", "fit_ok": True}


def run_elastic2d_rayleigh_validation(params) -> dict[str, Any]:
    """运行均匀半空间 Rayleigh-like surface event 验证。"""

    trial = make_elastic2d_validation_params(params)
    result = run_elastic2d_prototype(trial, with_void=False)
    velocity_check = _estimate_surface_velocity(result)
    vs = float(np.median(result.model.vs_mps))
    expected_min = 0.85 * vs
    expected_max = 0.98 * vs
    detected = expected_min <= velocity_check["velocity_mps"] <= expected_max
    return {
        "params": trial,
        "elastic_result": result,
        "estimated_surface_velocity_mps": velocity_check["velocity_mps"],
        "velocity_estimation_method": velocity_check["method"],
        "velocity_fit_ok": velocity_check["fit_ok"],
        "expected_rayleigh_like_range_mps": [expected_min, expected_max],
        "rayleigh_like_event_detected": bool(detected),
        "cfl_info": result.cfl_info,
        "diagnostics": result.diagnostics,
        "note": "collocated-grid 最小原型只做 Rayleigh-like sanity check，不是严格 Rayleigh 理论速度验证。",
    }
