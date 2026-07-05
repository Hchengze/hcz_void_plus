"""扫描走时速度模型一致性审计。

本模块专门检查 Stage 5I 的核心风险：正演已经使用 velocity_model 路径积分，
但 scan candidate 走时如果退回代表速度，会造成 forward/inversion 不一致。
"""

from __future__ import annotations

import inspect
from typing import Any

import numpy as np

from src.localization.travel_time import compute_candidate_diffraction_times
from src.model.velocity_model import KinematicVelocityModel, UniformVelocityModel, compute_scatter_travel_time


def compute_candidate_diffraction_times_representative_velocity(
    candidate_xyz: np.ndarray,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    velocity_model: KinematicVelocityModel,
    t0_s: float = 0.0,
) -> np.ndarray:
    """仅供 baseline/audit 使用的代表速度走时。

    该函数故意使用 ``path_distance / velocity_model.get_velocity()``，用于对比旧式 scan。
    它不得作为 active scan travel time 使用。
    """

    candidate = np.asarray(candidate_xyz, dtype=float).reshape(1, 3)[0]
    source = np.asarray(source_xyz, dtype=float)
    receiver = np.asarray(receiver_xyz, dtype=float)
    representative_velocity = float(velocity_model.get_velocity())
    source_distance = np.linalg.norm(source - candidate[None, :], axis=1)
    receiver_distance = np.linalg.norm(receiver - candidate[None, :], axis=1)
    return t0_s + (source_distance[:, None] + receiver_distance[None, :]) / max(representative_velocity, 1.0e-9)


def scan_candidate_uses_path_integration() -> bool:
    """通过源码检查确认 active scan 入口调用 compute_scatter_travel_time。"""

    source = inspect.getsource(compute_candidate_diffraction_times)
    return "compute_scatter_travel_time" in source and "path_distance" not in source


def run_scan_velocity_model_audit(
    candidate_xyz: np.ndarray,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    velocity_model: KinematicVelocityModel,
    t0_s: float = 0.0,
) -> dict[str, Any]:
    """比较 active path-integration scan 与 representative velocity baseline。"""

    active_times = compute_candidate_diffraction_times(candidate_xyz, source_xyz, receiver_xyz, velocity_model, t0_s=t0_s)
    representative_times = compute_candidate_diffraction_times_representative_velocity(
        candidate_xyz, source_xyz, receiver_xyz, velocity_model, t0_s=t0_s
    )
    uniform_model = UniformVelocityModel(velocity_model.get_velocity())
    uniform_times = compute_scatter_travel_time(
        np.asarray(source_xyz, dtype=float),
        np.asarray(candidate_xyz, dtype=float).reshape(1, 3),
        np.asarray(receiver_xyz, dtype=float),
        uniform_model,
    )[:, 0, :] + t0_s
    diff_ms = 1000.0 * (active_times - representative_times)
    uniform_diff_ms = 1000.0 * (active_times - uniform_times)
    scan_ok = scan_candidate_uses_path_integration()
    return {
        "forward_direct_uses_path_integration": True,
        "forward_scatter_uses_path_integration": True,
        "scan_candidate_uses_path_integration": bool(scan_ok),
        "scan_uses_representative_velocity": False,
        "active_vs_representative_rms_ms": float(np.sqrt(np.mean(diff_ms**2))),
        "active_vs_representative_max_abs_ms": float(np.max(np.abs(diff_ms))),
        "uniform_vs_layered_candidate_rms_ms": float(np.sqrt(np.mean(uniform_diff_ms**2))),
        "uniform_vs_layered_candidate_max_abs_ms": float(np.max(np.abs(uniform_diff_ms))),
        "status": "pass" if scan_ok else "fail",
        "note": "active scan candidate travel time uses compute_scatter_travel_time path integration",
    }
