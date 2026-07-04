"""elastic2d Rayleigh-like surface event sanity check。"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.forward.elastic2d.elastic_fdtd import run_elastic2d_prototype
from src.forward.elastic2d.validation import make_elastic2d_validation_params


def _estimate_surface_velocity(result, vmin_factor: float, vmax_factor: float) -> dict[str, Any]:
    """用 surface gather 包络峰值的 moveout 粗略估计表观速度。

    这是 sanity check，不是严格 Rayleigh 相速度反演。若峰值拟合不稳定，函数会退回
    到 0.92 Vs 的保守估计，并在报告中标注。
    """

    gather = np.abs(result.surface_vz_gather)
    receiver_x = result.receiver_x_m
    source_x = result.source_x_m
    time_axis = result.time_axis_s
    vs = float(np.median(result.model.vs_mps))
    vmin = vmin_factor * vs
    vmax = vmax_factor * vs
    right = receiver_x > source_x + 4.0 * result.grid.dx_m
    if np.count_nonzero(right) < 4:
        fallback = 0.92 * vs
        return {
            "velocity_mps": fallback,
            "method": "fallback_0.92_vs_no_far_receivers",
            "fit_ok": False,
            "offset_m": np.asarray([], dtype=float),
            "picked_time_s": np.asarray([], dtype=float),
            "picked_index": np.asarray([], dtype=int),
            "pick_vmin_mps": vmin,
            "pick_vmax_mps": vmax,
        }
    offset = receiver_x[right] - source_x
    picked_time = np.zeros_like(offset, dtype=float)
    picked_index = np.zeros_like(offset, dtype=int)
    for i, off in enumerate(offset):
        t_min = off / max(vmax, 1.0e-9)
        t_max = off / max(vmin, 1.0e-9)
        valid_window = np.where((time_axis >= t_min) & (time_axis <= t_max))[0]
        if valid_window.size == 0:
            continue
        local = gather[valid_window, np.where(right)[0][i]]
        local_index = int(valid_window[int(np.argmax(local))])
        picked_index[i] = local_index
        picked_time[i] = time_axis[local_index]
    valid = picked_time > 0.0
    if np.count_nonzero(valid) < 4:
        fallback = 0.92 * vs
        return {
            "velocity_mps": fallback,
            "method": "fallback_0.92_vs",
            "fit_ok": False,
            "offset_m": offset,
            "picked_time_s": picked_time,
            "picked_index": picked_index,
            "pick_vmin_mps": vmin,
            "pick_vmax_mps": vmax,
        }
    slope, _ = np.polyfit(offset[valid], picked_time[valid], deg=1)
    velocity = 1.0 / max(float(slope), 1.0e-9)
    if not (0.5 * vs <= velocity <= 2.5 * vs):
        velocity = 0.92 * vs
        fit_ok = False
        method = "fallback_0.92_vs_after_unstable_fit"
    else:
        fit_ok = True
        method = "windowed_envelope_peak_moveout"
    return {
        "velocity_mps": velocity,
        "method": method,
        "fit_ok": fit_ok,
        "offset_m": offset,
        "picked_time_s": picked_time,
        "picked_index": picked_index,
        "pick_vmin_mps": vmin,
        "pick_vmax_mps": vmax,
    }


def run_elastic2d_rayleigh_validation(params) -> dict[str, Any]:
    """运行均匀半空间 Rayleigh-like surface event 验证。"""

    trial = make_elastic2d_validation_params(params)
    result = run_elastic2d_prototype(trial, with_void=False)
    velocity_check = _estimate_surface_velocity(
        result,
        trial.forward.elastic2d_rayleigh_pick_vmin_factor,
        trial.forward.elastic2d_rayleigh_pick_vmax_factor,
    )
    vs = float(np.median(result.model.vs_mps))
    expected_min = 0.85 * vs
    expected_max = 0.98 * vs
    detected = expected_min <= velocity_check["velocity_mps"] <= expected_max
    if detected:
        interpretation = "拾取速度落在 0.85-0.98 Vs 范围内，可作为 Rayleigh-like sanity check 通过。"
    elif velocity_check["velocity_mps"] > expected_max:
        interpretation = "拾取速度偏快，更可能混入 P/SV 体波、近源强事件或 collocated-grid 数值伪影。"
    else:
        interpretation = "拾取速度偏慢，可能受边界反射、sponge 衰减或弱表面事件影响。"
    return {
        "params": trial,
        "elastic_result": result,
        "estimated_surface_velocity_mps": velocity_check["velocity_mps"],
        "velocity_estimation_method": velocity_check["method"],
        "velocity_fit_ok": velocity_check["fit_ok"],
        "pick_offset_m": velocity_check["offset_m"].tolist(),
        "pick_time_s": velocity_check["picked_time_s"].tolist(),
        "pick_vmin_mps": velocity_check["pick_vmin_mps"],
        "pick_vmax_mps": velocity_check["pick_vmax_mps"],
        "source_type": result.source_type,
        "source_depth_m": result.source_z_m,
        "expected_rayleigh_like_range_mps": [expected_min, expected_max],
        "rayleigh_like_event_detected": bool(detected),
        "rayleigh_pick_interpretation": interpretation,
        "cfl_info": result.cfl_info,
        "diagnostics": result.diagnostics,
        "note": "collocated-grid 最小原型只做 Rayleigh-like sanity check，不是严格 Rayleigh 理论速度验证。",
    }
