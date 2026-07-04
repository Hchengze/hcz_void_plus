"""staggered-grid elastic2d 诊断。"""

from __future__ import annotations

from typing import Any

import numpy as np


def check_staggered_elastic_cfl(vp_mps: np.ndarray, dt_s: float, dx_m: float, dz_m: float) -> dict[str, Any]:
    """检查 staggered-grid elastic FDTD CFL。"""

    vmax = float(np.max(vp_mps))
    cfl = vmax * dt_s * np.sqrt(1.0 / dx_m**2 + 1.0 / dz_m**2)
    return {"cfl_number": cfl, "stable": bool(cfl < 0.5), "vmax_mps": vmax}


def staggered_energy_diagnostics(surface_gather: np.ndarray, snapshots: np.ndarray) -> dict[str, float]:
    """输出最小能量诊断。"""

    return {
        "surface_rms": float(np.sqrt(np.mean(surface_gather**2))),
        "surface_max_abs": float(np.max(np.abs(surface_gather))),
        "snapshot_max_abs": float(np.max(np.abs(snapshots))) if snapshots.size else 0.0,
    }
