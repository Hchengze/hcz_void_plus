"""速度模型消融实验。

Stage 5A 的目标不是实现真实三维弹性波场，而是验证：当 forward 与 scan 使用
uniform、layered、横向梯度或局部低速区等不同等效速度模型时，绕射走时和定位结果
会怎样变化。所有实验仍采用 source_xyz / receiver_xyz / candidate_xyz 的三维运动学
几何和 straight-ray travel-time 积分。
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from src.features.direct_arrival import predict_direct_arrival_times
from src.features.direct_wave_mute import mute_direct_wave
from src.forward.multishot_forward import synthesize_multishot_forward
from src.localization.multishot_scan import run_multishot_scan
from src.localization.travel_time import compute_candidate_diffraction_times
from src.model.velocity_model import build_velocity_model
from src.preprocessing.preprocessing_pipeline import run_preprocessing_pipeline
from src.validation.common import clone_params, make_diagnostic_scan_grid, summarize_volume


VELOCITY_CASES = [
    "uniform",
    "layered",
    "lateral_gradient",
    "localized_low_velocity_zone",
    "layered_with_anomaly_perturbation",
]


def _params_for_velocity_case(params: SimpleNamespace, model_type: str) -> SimpleNamespace:
    """生成某个速度模型案例的参数副本。

    所有参数仍来自 main.py 解析后的 params；这里仅在验证实验中修改副本，不会建立
    第二套配置文件。局部低速案例会显式启用 low_velocity_zone，避免名义上选择了
    localized_low_velocity_zone 但实际无扰动。
    """

    trial = clone_params(params)
    trial.velocity.model_type = model_type
    if model_type == "lateral_gradient":
        trial.velocity.lateral_gradient_x_mps_per_m = 0.15
        trial.velocity.lateral_gradient_y_mps_per_m = -1.5
    if model_type in {"localized_low_velocity_zone", "layered_with_anomaly_perturbation"}:
        trial.velocity.low_velocity_zone_enabled = True
        trial.velocity.low_velocity_zone_x0_m = params.anomaly.x0_m
        trial.velocity.low_velocity_zone_y0_m = params.anomaly.y0_m
        trial.velocity.low_velocity_zone_depth_m = params.anomaly.depth_m
        trial.velocity.low_velocity_zone_radius_m = max(2.5, params.anomaly.radius_m * 2.0)
        trial.velocity.low_velocity_factor = min(params.velocity.low_velocity_factor, 0.7)
    trial.scan.score_mode = "energy"
    trial.scan.score_method = "diffraction_energy_stack"
    trial.scan.active_score_kind = "unweighted"
    return trial


def _run_single_case(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
    model_type: str,
) -> dict[str, Any]:
    """对一个速度模型完成 forward + preprocessing + direct mute + scan。"""

    trial = _params_for_velocity_case(params, model_type)
    velocity_model = build_velocity_model(trial)
    scan_grid = make_diagnostic_scan_grid(trial)
    synthetic = synthesize_multishot_forward(
        trial,
        source_xyz,
        receiver_xyz,
        scatter_xyz,
        scatter_weight,
        velocity_model,
    )["synthetic_data"]
    processed, preprocessing_info = run_preprocessing_pipeline(synthetic, trial)
    direct_times = predict_direct_arrival_times(trial, source_xyz, receiver_xyz, velocity_model)
    scan_data = mute_direct_wave(
        processed,
        trial.derived.time_axis,
        direct_times,
        trial.scan.direct_mute_half_width_s,
        mode=trial.scan.direct_mute_mode,
    )
    scan_result = run_multishot_scan(
        scan_data,
        trial.derived.time_axis,
        source_xyz,
        receiver_xyz,
        velocity_model,
        scan_grid,
        trial,
    )
    summary = summarize_volume(trial, scan_result["score_volume_unweighted"], scan_grid)

    truth_xyz = np.array([trial.anomaly.x0_m, trial.anomaly.y0_m, trial.anomaly.depth_m], dtype=float)
    model_times = compute_candidate_diffraction_times(truth_xyz, source_xyz, receiver_xyz, velocity_model, trial.time.t0_s)
    uniform_trial = _params_for_velocity_case(params, "uniform")
    uniform_model = build_velocity_model(uniform_trial)
    uniform_times = compute_candidate_diffraction_times(truth_xyz, source_xyz, receiver_xyz, uniform_model, trial.time.t0_s)
    residual = model_times - uniform_times

    return {
        "model_type": model_type,
        "best_location": summary["best_location"],
        "truth_error": summary["truth_error"],
        "x_span_m": summary["x_span_m"],
        "y_span_m": summary["y_span_m"],
        "depth_span_m": summary["depth_span_m"],
        "high_score_region_point_count": summary["high_score_region_point_count"],
        "high_score_component_count": summary["high_score_component_count"],
        "recommended_location_type": "uncertainty_interval"
        if summary["y_span_m"] > 0.0 or summary["depth_span_m"] > 0.0
        else "single_candidate",
        "confidence_flag": "low"
        if summary["y_span_m"] >= trial.confidence.coupling_warning_span_y_m
        or summary["depth_span_m"] >= trial.confidence.coupling_warning_span_depth_m
        else "medium",
        "travel_time_residual_to_uniform_mean_s": float(np.mean(residual)),
        "travel_time_residual_to_uniform_rms_s": float(np.sqrt(np.mean(residual**2))),
        "preprocessing_info": preprocessing_info,
    }


def run_velocity_model_ablation(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
) -> dict[str, Any]:
    """运行 uniform/layered/heterogeneous 速度模型消融。"""

    cases = {
        model_type: _run_single_case(params, source_xyz, receiver_xyz, scatter_xyz, scatter_weight, model_type)
        for model_type in VELOCITY_CASES
    }
    best_error_case = min(cases, key=lambda name: cases[name]["truth_error"]["distance_m"])
    best_depth_case = min(cases, key=lambda name: abs(cases[name]["truth_error"]["ddepth_m"]))
    largest_residual_case = max(cases, key=lambda name: abs(cases[name]["travel_time_residual_to_uniform_mean_s"]))
    return {
        "cases": cases,
        "best_truth_error_case": best_error_case,
        "best_depth_case": best_depth_case,
        "largest_travel_time_residual_case": largest_residual_case,
        "note": "速度模型消融使用 straight-ray kinematic approximation，不是弹性波反演。",
    }
