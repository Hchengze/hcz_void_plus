"""elastic2d 数值诊断。"""

from __future__ import annotations

import numpy as np


def elastic_cfl_number(vp_mps: np.ndarray, dt_s: float, dx_m: float, dz_m: float) -> float:
    """计算 collocated-grid 原型的保守 CFL 数。"""

    vmax = float(np.max(vp_mps))
    return vmax * dt_s * np.sqrt(1.0 / dx_m**2 + 1.0 / dz_m**2)


def check_elastic_cfl(vp_mps: np.ndarray, dt_s: float, dx_m: float, dz_m: float) -> dict[str, float | bool]:
    """返回 CFL 稳定性诊断。

    collocated-grid elastic 原型采用保守阈值 0.45。后续若改为 staggered-grid，需要重新
    标定稳定条件。
    """

    cfl = elastic_cfl_number(vp_mps, dt_s, dx_m, dz_m)
    return {"cfl_number": cfl, "stable": bool(cfl < 0.45), "recommended_max": 0.45}


def elastic_energy_diagnostics(surface_gather: np.ndarray, snapshots: np.ndarray) -> dict[str, float]:
    """输出能量和最大振幅诊断。"""

    return {
        "surface_gather_energy": float(np.mean(surface_gather * surface_gather)) if surface_gather.size else 0.0,
        "max_abs_surface": float(np.max(np.abs(surface_gather))) if surface_gather.size else 0.0,
        "max_abs_snapshot": float(np.max(np.abs(snapshots))) if snapshots.size else 0.0,
    }
