"""elastic2d void-like scattering validation。"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.forward.elastic2d.elastic_fdtd import run_elastic2d_prototype
from src.forward.elastic2d.validation import make_elastic2d_validation_params
from src.validation.common import clone_params


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


def run_elastic2d_void_parameter_sensitivity(params) -> dict[str, Any]:
    """运行 void-like 参数敏感性。

    该函数使用轻量 validation 网格，比较 Vs 折减、扰动半径和震源方向对 residual
    energy 的影响。它不是弹性参数反演，只用于判断当前 elastic2d_prototype 的
    void residual 是否具有可解释的参数趋势。
    """

    vs_factors = [0.2, 0.4, 0.6]
    radii = [0.5, 1.0, 1.5]
    source_types = ["vertical_force", "horizontal_force"]
    cases: dict[str, dict[str, Any]] = {}
    background_cache: dict[str, Any] = {}
    for source_type in source_types:
        base = clone_params(params)
        base.forward.elastic2d_source_type = source_type
        trial = make_elastic2d_validation_params(base)
        background_cache[source_type] = run_elastic2d_prototype(trial, with_void=False)
        for radius in radii:
            for factor in vs_factors:
                case_params = clone_params(trial)
                case_params.forward.elastic2d_void_radius_m = radius
                case_params.forward.elastic2d_void_vs_factor = factor
                anomaly = run_elastic2d_prototype(case_params, with_void=True)
                background = background_cache[source_type]
                residual = anomaly.surface_vz_gather - background.surface_vz_gather
                residual_energy = float(np.mean(residual * residual))
                background_energy = float(np.mean(background.surface_vz_gather * background.surface_vz_gather))
                name = f"{source_type}_r{radius}_vs{factor}"
                cases[name] = {
                    "source_type": source_type,
                    "void_radius_m": radius,
                    "void_vs_factor": factor,
                    "residual_energy": residual_energy,
                    "relative_residual_energy": residual_energy / max(background_energy, 1.0e-12),
                }
    best_case = max(cases, key=lambda key: cases[key]["residual_energy"])
    return {
        "cases": cases,
        "best_case": best_case,
        "best_residual_energy": cases[best_case]["residual_energy"],
        "best_relative_residual_energy": cases[best_case]["relative_residual_energy"],
        "parameter_count": len(cases),
        "note": "该敏感性只检查 low-Vs/low-density perturbation 的 residual 能量，不代表真实空腔边界散射强度。",
    }
