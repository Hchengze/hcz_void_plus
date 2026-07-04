"""elastic2d DAS-like 分量和 gauge length 诊断。"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.forward.elastic2d.das_response import build_elastic_das_response, compute_gauge_length_strain
from src.forward.elastic2d.elastic_fdtd import run_elastic2d_prototype
from src.forward.elastic2d.validation import make_elastic2d_validation_params
from src.validation.common import clone_params


def _rms(value: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(value, dtype=float) ** 2)))


def run_elastic2d_das_component_response(params) -> dict[str, Any]:
    """比较 vx、vz 和 gauge strain 的响应强度。

    DAS-like gauge strain 沿光纤切向近似，因此更依赖 surface vx。若 vertical_force
    下 vx 很弱，报告必须诚实说明；horizontal_force 只用于 validation，不能替代真实
    道路锤击源。
    """

    source_cases = {}
    for source_type in ["vertical_force", "horizontal_force"]:
        case_params = clone_params(params)
        case_params.forward.elastic2d_source_type = source_type
        trial = make_elastic2d_validation_params(case_params)
        result = run_elastic2d_prototype(trial, with_void=False)
        gauge = compute_gauge_length_strain(
            result.surface_vx_gather,
            result.grid.dx_m,
            params.das_like.gauge_length_m,
        )
        source_cases[source_type] = {
            "vx_rms": _rms(result.surface_vx_gather),
            "vz_rms": _rms(result.surface_vz_gather),
            "gauge_strain_rms": _rms(gauge),
            "source_depth_m": result.source_z_m,
        }

    gauge_lengths = [0.5, 1.0, 2.0, 4.0]
    horizontal_params = clone_params(params)
    horizontal_params.forward.elastic2d_source_type = "horizontal_force"
    horizontal_trial = make_elastic2d_validation_params(horizontal_params)
    horizontal_result = run_elastic2d_prototype(horizontal_trial, with_void=False)
    gauge_length_cases = {}
    for length in gauge_lengths:
        strain = compute_gauge_length_strain(horizontal_result.surface_vx_gather, horizontal_result.grid.dx_m, length)
        gauge_length_cases[str(length)] = {
            "gauge_length_m": length,
            "gauge_strain_rms": _rms(strain),
        }

    void_background = run_elastic2d_prototype(horizontal_trial, with_void=False)
    void_anomaly = run_elastic2d_prototype(horizontal_trial, with_void=True)
    bg_strain = compute_gauge_length_strain(
        void_background.surface_vx_gather,
        void_background.grid.dx_m,
        params.das_like.gauge_length_m,
    )
    an_strain = compute_gauge_length_strain(
        void_anomaly.surface_vx_gather,
        void_anomaly.grid.dx_m,
        params.das_like.gauge_length_m,
    )
    residual_strain = an_strain - bg_strain
    best_source = max(source_cases, key=lambda key: source_cases[key]["gauge_strain_rms"])
    best_gauge = max(gauge_length_cases, key=lambda key: gauge_length_cases[key]["gauge_strain_rms"])
    response = build_elastic_das_response(
        horizontal_result.surface_vx_gather,
        horizontal_result.surface_vz_gather,
        horizontal_result.grid.dx_m,
        params.das_like.gauge_length_m,
    )
    return {
        "source_cases": source_cases,
        "gauge_length_cases": gauge_length_cases,
        "best_source_type_for_gauge": best_source,
        "best_gauge_length_m": gauge_length_cases[best_gauge]["gauge_length_m"],
        "point_shape": tuple(int(v) for v in response["point_receiver_gather"].shape),
        "strain_shape": tuple(int(v) for v in response["gauge_length_strain_gather"].shape),
        "strain_to_point_rms_ratio": _rms(response["gauge_length_strain_gather"])
        / max(_rms(response["point_receiver_gather"]), 1.0e-12),
        "gauge_void_residual_rms": _rms(residual_strain),
        "status": "component_and_gauge_length_checked",
        "note": "当前 DAS-like strain 是 surface vx 的有限差分近似，不是真实 DAS 仪器响应。",
    }
