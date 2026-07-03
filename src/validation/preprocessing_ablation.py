"""预处理组合消融验证。

该模块比较不同预处理组合对三维运动学扫描结果的影响。为保持本地快速可跑，
默认使用三维子采样诊断网格；主流程正式 scan_result 不受影响。
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from src.features.direct_wave_mute import mute_direct_wave
from src.localization.multishot_scan import run_multishot_scan
from src.localization.travel_time import compute_candidate_diffraction_times
from src.preprocessing.preprocessing_pipeline import run_preprocessing_pipeline
from src.validation.common import clone_params, make_diagnostic_scan_grid


def _curve_energy_ratio(
    data: np.ndarray,
    time_axis: np.ndarray,
    curve_times: np.ndarray,
    half_width_s: float,
) -> float:
    """计算一组理论曲线附近能量占全记录能量的比例。"""

    dt = float(time_axis[1] - time_axis[0]) if len(time_axis) > 1 else 1.0
    half_samples = int(np.ceil(half_width_s / dt))
    center_index = np.rint((curve_times - time_axis[0]) / dt).astype(int)
    total_energy = float(np.sum(data * data)) + 1.0e-12
    curve_energy = 0.0
    n_shot, n_time, n_channel = data.shape
    for i_shot in range(n_shot):
        for i_channel in range(n_channel):
            start = max(0, center_index[i_shot, i_channel] - half_samples)
            stop = min(n_time, center_index[i_shot, i_channel] + half_samples + 1)
            if stop > start:
                window = data[i_shot, start:stop, i_channel]
                curve_energy += float(np.sum(window * window))
    return float(curve_energy / total_energy)


def _configure_preprocessing_case(params: SimpleNamespace, case_name: str) -> SimpleNamespace:
    """根据消融组合生成独立 params 副本。"""

    trial = clone_params(params)
    trial.preprocessing.enabled = case_name != "none"
    trial.preprocessing.bandpass_enabled = "bandpass" in case_name
    trial.preprocessing.trace_normalization = "rms" if "trace_normalization" in case_name else "none"
    trial.preprocessing.fk_filter_enabled = "fk_filter" in case_name
    trial.preprocessing.envelope_enabled = "envelope" in case_name
    trial.preprocessing.agc_enabled = False
    trial.scan.direct_mute_enabled = "taper_direct_mute" in case_name
    trial.scan.direct_mute_mode = "taper"
    trial.scan.score_mode = "energy"
    trial.scan.score_method = "diffraction_energy_stack"
    trial.scan.active_score_kind = "unweighted"
    return trial


def run_preprocessing_ablation(
    params: SimpleNamespace,
    synthetic_data: np.ndarray,
    direct_times: np.ndarray,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    velocity_model: Any,
) -> dict[str, Any]:
    """运行 Stage 4B 预处理组合消融。

    输出的 best 和不确定性跨度来自三维诊断网格。报告中必须解释：该消融用于
    比较预处理方向，不替代主 full_pipeline 的正式扫描结果。
    """

    cases = [
        "none",
        "bandpass",
        "bandpass_trace_normalization",
        "bandpass_trace_normalization_taper_direct_mute",
        "bandpass_trace_normalization_fk_filter",
        "bandpass_trace_normalization_envelope",
    ]
    scan_grid = make_diagnostic_scan_grid(params)
    truth_xyz = np.array([params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m], dtype=float)
    truth_times = compute_candidate_diffraction_times(
        truth_xyz,
        source_xyz,
        receiver_xyz,
        velocity_model,
        t0_s=params.time.t0_s,
    )
    results: dict[str, Any] = {}
    for case_name in cases:
        trial = _configure_preprocessing_case(params, case_name)
        processed, info = run_preprocessing_pipeline(synthetic_data, trial)
        scan_data = processed
        if trial.scan.direct_mute_enabled:
            scan_data = mute_direct_wave(
                scan_data,
                params.derived.time_axis,
                direct_times,
                params.scan.direct_mute_half_width_s,
                mode="taper",
            )
        scan_result = run_multishot_scan(
            scan_data,
            params.derived.time_axis,
            source_xyz,
            receiver_xyz,
            velocity_model,
            scan_grid,
            trial,
        )
        high_region = scan_result["score_volume_unweighted"]
        from src.validation.common import summarize_volume

        summary = summarize_volume(trial, high_region, scan_grid)
        direct_ratio = _curve_energy_ratio(scan_data, params.derived.time_axis, direct_times, params.scan.direct_mute_half_width_s)
        diffraction_ratio = _curve_energy_ratio(
            scan_data,
            params.derived.time_axis,
            truth_times,
            params.scan.time_window_half_width_s,
        )
        results[case_name] = {
            "preprocessing_info": info,
            "best_location": summary["best_location"],
            "truth_error": summary["truth_error"],
            "x_span_m": summary["x_span_m"],
            "y_span_m": summary["y_span_m"],
            "depth_span_m": summary["depth_span_m"],
            "high_score_region_point_count": summary["high_score_region_point_count"],
            "high_score_component_count": summary["high_score_component_count"],
            "diffraction_curve_energy_ratio": diffraction_ratio,
            "direct_wave_residual_ratio": direct_ratio,
            "low_confidence_flag": "low"
            if summary["y_span_m"] >= params.confidence.coupling_warning_span_y_m
            or summary["depth_span_m"] >= params.confidence.coupling_warning_span_depth_m
            else "medium",
        }
    best_case = min(results, key=lambda name: results[name]["truth_error"]["distance_m"])
    narrow_case = min(results, key=lambda name: (results[name]["y_span_m"] + results[name]["depth_span_m"]))
    return {
        "cases": results,
        "best_truth_error_case": best_case,
        "narrowest_y_depth_case": narrow_case,
        "scan_grid_shape": (
            len(scan_grid["x_grid"]),
            len(scan_grid["y_grid"]),
            len(scan_grid["depth_grid"]),
        ),
        "note": "预处理消融使用轻量三维诊断网格，不是大规模鲁棒性扫描。",
    }

