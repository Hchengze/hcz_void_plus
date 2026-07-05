"""elastic2d DAS-like 分量和 gauge length 诊断。"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.forward.elastic2d.das_response import (
    accumulate_displacement_like,
    build_elastic_das_response,
    compute_gauge_length_strain,
    compute_pairwise_gauge_strain,
)
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


def run_elastic2d_das_nonzero_check(params) -> dict[str, Any]:
    """检查 DAS-like gauge strain 为零/很弱的原因。

    该诊断同时比较 vx、vz、ux-like 位移累积量、速度型 gauge strain 和位移型 gauge
    strain。若所有 gauge 指标仍接近零，报告必须禁止把 gauge strain 默认纳入定位。
    """

    source_types = ["vertical_force", "horizontal_force"]
    gauge_lengths = [0.5, 1.0, 2.0, 4.0]
    cases: dict[str, dict[str, Any]] = {}
    threshold = 1.0e-18
    for source_type in source_types:
        trial_params = clone_params(params)
        trial_params.forward.elastic2d_source_type = source_type
        trial = make_elastic2d_validation_params(trial_params)
        result = run_elastic2d_prototype(trial, with_void=False)
        dt = float(result.time_axis_s[1] - result.time_axis_s[0]) if len(result.time_axis_s) > 1 else params.time.dt_s
        ux_like = accumulate_displacement_like(result.surface_vx_gather, dt)
        for gauge_length in gauge_lengths:
            velocity_pair = compute_pairwise_gauge_strain(result.surface_vx_gather, result.grid.dx_m, gauge_length)
            displacement_pair = compute_pairwise_gauge_strain(ux_like, result.grid.dx_m, gauge_length)
            name = f"{source_type}_g{gauge_length}"
            cases[name] = {
                "source_type": source_type,
                "gauge_length_m": gauge_length,
                "vx_rms": _rms(result.surface_vx_gather),
                "vz_rms": _rms(result.surface_vz_gather),
                "ux_like_rms": _rms(ux_like),
                "velocity_gauge_strain_rms": _rms(velocity_pair["strain"]),
                "displacement_gauge_strain_rms": _rms(displacement_pair["strain"]),
                "gauge_samples": velocity_pair["gauge_samples"],
                "pair_count": velocity_pair["pair_count"],
                "receiver_spacing_m": velocity_pair["receiver_spacing_m"],
            }
    best_velocity = max(cases, key=lambda key: cases[key]["velocity_gauge_strain_rms"])
    best_displacement = max(cases, key=lambda key: cases[key]["displacement_gauge_strain_rms"])
    best_metric = max(
        cases[best_velocity]["velocity_gauge_strain_rms"],
        cases[best_displacement]["displacement_gauge_strain_rms"],
    )
    if best_metric <= threshold:
        reason = "gauge strain 仍接近零，可能是 surface vx 极弱、pair 差分抵消或 collocated-grid 表面响应不足。"
    elif cases[best_velocity]["vx_rms"] <= threshold:
        reason = "surface vx 极弱，gauge 响应不应进入默认定位。"
    else:
        reason = "gauge strain 非零，但仍只属于 DAS-like validation，不是真实 DAS 仪器响应。"
    best_case = cases[best_velocity]
    return {
        "cases": cases,
        "best_velocity_gauge_case": best_velocity,
        "best_displacement_gauge_case": best_displacement,
        "best_velocity_gauge_rms": cases[best_velocity]["velocity_gauge_strain_rms"],
        "best_displacement_gauge_rms": cases[best_displacement]["displacement_gauge_strain_rms"],
        "best_velocity_gauge_source_type": best_case["source_type"],
        "best_velocity_gauge_length_m": best_case["gauge_length_m"],
        "das_gauge_nonzero_status": "nonzero" if best_metric > threshold else "zero_or_too_weak",
        # 即使本轮诊断能得到非零 gauge strain，它仍没有通过真实 DAS gauge length、
        # 光纤方向、仪器响应和 elastic2d 数值格式校准，因此默认定位仍禁止使用。
        "default_localization_should_use_gauge_strain": False,
        "diagnosis": reason,
        "old_relative_metric_zero_reason": (
            "旧指标使用 strain_rms / point_rms，相对量会被强 point receiver 分量和极小 "
            "gauge 有限差分同时压低，格式化或阈值判断时可能显示为 0。"
        ),
        "absolute_nonzero_reason": (
            "Stage 5H 改看 velocity gauge strain 的绝对 RMS，并使用非零 receiver pair；"
            "因此能识别弱非零响应，但这不等于已具备定位解释力。"
        ),
        "required_for_real_das": [
            "光纤局部切向方向",
            "gauge length 校准",
            "仪器响应",
            "真实接收道距",
            "弹性波场中合适的水平分量或轴向应变",
        ],
        "threshold": threshold,
        "note": "即使 gauge strain 非零，也必须经过真实 DAS gauge/方向/仪器响应校准后才能用于主定位。",
    }
