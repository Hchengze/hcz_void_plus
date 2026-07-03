"""acoustic2d 稳定性与振幅诊断。"""

from __future__ import annotations

import numpy as np


def compute_cfl_number(velocity_mps: np.ndarray, dt_s: float, dx_m: float, dz_m: float) -> float:
    """计算二维声学二阶差分的 CFL 数。"""

    vmax = float(np.max(velocity_mps))
    return vmax * dt_s * np.sqrt(1.0 / dx_m**2 + 1.0 / dz_m**2)


def check_cfl_stability(velocity_mps: np.ndarray, dt_s: float, dx_m: float, dz_m: float) -> dict[str, float | bool]:
    """返回 CFL 稳定性诊断。

    对二维二阶 acoustic FDTD，CFL 小于约 1 是必要条件；这里保守使用 0.7。
    """

    cfl = compute_cfl_number(velocity_mps, dt_s, dx_m, dz_m)
    return {"cfl": cfl, "cfl_number": cfl, "stable": bool(cfl < 0.7), "recommended_max": 0.7}


def acoustic_energy_diagnostics(wavefield_snapshots: np.ndarray, shot_gather: np.ndarray) -> dict[str, float]:
    """输出最大振幅和能量诊断，帮助发现数值爆炸。"""

    max_abs_wavefield = float(np.max(np.abs(wavefield_snapshots))) if wavefield_snapshots.size else 0.0
    max_abs_gather = float(np.max(np.abs(shot_gather))) if shot_gather.size else 0.0
    gather_energy = float(np.mean(shot_gather * shot_gather)) if shot_gather.size else 0.0
    return {
        "max_abs_amplitude": max(max_abs_wavefield, max_abs_gather),
        "energy": gather_energy,
        "max_abs_wavefield": float(np.max(np.abs(wavefield_snapshots))) if wavefield_snapshots.size else 0.0,
        "max_abs_gather": float(np.max(np.abs(shot_gather))) if shot_gather.size else 0.0,
        "gather_energy": float(np.mean(shot_gather * shot_gather)) if shot_gather.size else 0.0,
    }
