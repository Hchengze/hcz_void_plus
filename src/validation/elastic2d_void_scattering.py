"""elastic2d void-like scattering validation。"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.forward.elastic2d.elastic_fdtd import run_elastic2d_prototype
from src.forward.elastic2d.validation import make_elastic2d_validation_params


def _local_kinematic_curve(result, velocity_mps: float, scatter_x_m: float, scatter_z_m: float) -> np.ndarray:
    """生成局部 2D source-scatter-receiver 运动学绕射曲线。"""

    source = np.array([result.source_x_m, result.source_z_m], dtype=float)
    scatter = np.array([scatter_x_m, scatter_z_m], dtype=float)
    receivers = np.column_stack([result.receiver_x_m, np.zeros_like(result.receiver_x_m)])
    t_source = np.linalg.norm(source - scatter) / max(velocity_mps, 1.0e-9)
    t_receiver = np.linalg.norm(receivers - scatter[None, :], axis=1) / max(velocity_mps, 1.0e-9)
    return t_source + t_receiver


def run_elastic2d_void_scattering(params) -> dict[str, Any]:
    """对比背景和低速 void-like 模型的 surface gather 残差。"""

    trial = make_elastic2d_validation_params(params)
    background = run_elastic2d_prototype(trial, with_void=False)
    anomaly = run_elastic2d_prototype(trial, with_void=True)
    residual = anomaly.surface_vz_gather - background.surface_vz_gather
    residual_envelope = np.abs(residual)
    scatter_x = 0.62 * background.grid.width_m
    scatter_z = min(max(0.45 * background.grid.depth_m, 2.0 * background.grid.dz_m), background.grid.depth_m)
    curve = _local_kinematic_curve(
        background,
        velocity_mps=float(np.median(background.model.vs_mps)),
        scatter_x_m=scatter_x,
        scatter_z_m=scatter_z,
    )
    residual_energy = float(np.mean(residual * residual))
    background_energy = float(np.mean(background.surface_vz_gather * background.surface_vz_gather))
    return {
        "params": trial,
        "background_result": background,
        "anomaly_result": anomaly,
        "residual_gather": residual,
        "residual_envelope": residual_envelope,
        "kinematic_curve_s": curve,
        "scatter_x_m": scatter_x,
        "scatter_z_m": scatter_z,
        "residual_energy": residual_energy,
        "relative_residual_energy": residual_energy / max(background_energy, 1.0e-12),
        "void_residual_visible": bool(np.any(np.abs(residual) > 0.0)),
        "note": "void-like 模型是低 Vp/低 Vs/低密度扰动，不是真实空腔边界条件。",
    }
