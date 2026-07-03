"""正演模型与扫描模型错配实验。

真实道路介质不可能完全等于反演假设。Stage 5A 用小规模实验检查：如果 forward
数据来自 layered 或局部低速模型，而 scan 仍使用 uniform，会产生怎样的系统误差。
这一步比单纯展示某个 best_location 更重要，因为它直接暴露速度模型不确定性的风险。
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from src.features.direct_arrival import predict_direct_arrival_times
from src.features.direct_wave_mute import mute_direct_wave
from src.forward.multishot_forward import synthesize_multishot_forward
from src.localization.multishot_scan import run_multishot_scan
from src.model.velocity_model import build_velocity_model
from src.preprocessing.preprocessing_pipeline import run_preprocessing_pipeline
from src.validation.common import clone_params, make_diagnostic_scan_grid, summarize_volume
from src.validation.velocity_model_ablation import _params_for_velocity_case


MISMATCH_CASES = [
    ("uniform_forward_uniform_scan", "uniform", "uniform"),
    ("layered_forward_layered_scan", "layered", "layered"),
    ("layered_forward_uniform_scan", "layered", "uniform"),
    ("localized_low_velocity_forward_uniform_scan", "localized_low_velocity_zone", "uniform"),
    ("layered_perturbation_forward_layered_scan", "layered_with_anomaly_perturbation", "layered"),
]


def _run_mismatch_case(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
    case_name: str,
    forward_model_type: str,
    scan_model_type: str,
) -> dict[str, Any]:
    """运行一个 forward/scan 速度模型错配案例。"""

    forward_params = _params_for_velocity_case(params, forward_model_type)
    scan_params = _params_for_velocity_case(params, scan_model_type)
    scan_params.scan.score_mode = "energy"
    scan_params.scan.score_method = "diffraction_energy_stack"
    scan_params.scan.active_score_kind = "unweighted"

    forward_model = build_velocity_model(forward_params)
    scan_model = build_velocity_model(scan_params)
    synthetic = synthesize_multishot_forward(
        forward_params,
        source_xyz,
        receiver_xyz,
        scatter_xyz,
        scatter_weight,
        forward_model,
    )["synthetic_data"]
    processed, preprocessing_info = run_preprocessing_pipeline(synthetic, scan_params)
    # 直达波预测也使用 scan 模型，模拟真实反演流程中“用假设模型做预处理”的情况。
    direct_times = predict_direct_arrival_times(scan_params, source_xyz, receiver_xyz, scan_model)
    scan_data = mute_direct_wave(
        processed,
        scan_params.derived.time_axis,
        direct_times,
        scan_params.scan.direct_mute_half_width_s,
        mode=scan_params.scan.direct_mute_mode,
    )
    scan_grid = make_diagnostic_scan_grid(scan_params)
    scan_result = run_multishot_scan(
        scan_data,
        scan_params.derived.time_axis,
        source_xyz,
        receiver_xyz,
        scan_model,
        scan_grid,
        scan_params,
    )
    summary = summarize_volume(scan_params, scan_result["score_volume_unweighted"], scan_grid)
    return {
        "case_name": case_name,
        "forward_model_type": forward_model_type,
        "scan_model_type": scan_model_type,
        "best_location": summary["best_location"],
        "truth_error": summary["truth_error"],
        "x_span_m": summary["x_span_m"],
        "y_span_m": summary["y_span_m"],
        "depth_span_m": summary["depth_span_m"],
        "high_score_component_count": summary["high_score_component_count"],
        "low_confidence_flag": "low"
        if summary["y_span_m"] >= scan_params.confidence.coupling_warning_span_y_m
        or summary["depth_span_m"] >= scan_params.confidence.coupling_warning_span_depth_m
        else "medium",
        "preprocessing_info": preprocessing_info,
    }


def run_model_mismatch_experiment(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
) -> dict[str, Any]:
    """运行正演/扫描速度模型错配实验。"""

    cases = {
        case_name: _run_mismatch_case(
            params,
            source_xyz,
            receiver_xyz,
            scatter_xyz,
            scatter_weight,
            case_name,
            forward_model_type,
            scan_model_type,
        )
        for case_name, forward_model_type, scan_model_type in MISMATCH_CASES
    }
    safest_case = min(cases, key=lambda name: cases[name]["truth_error"]["distance_m"])
    riskiest_case = max(cases, key=lambda name: cases[name]["truth_error"]["distance_m"])
    return {
        "cases": cases,
        "safest_case": safest_case,
        "riskiest_case": riskiest_case,
        "minimum_recommended_velocity_model": "layered",
        "note": "若真实为 layered 而扫描仍假设 uniform，可能引入系统走时残差和 y-depth 不确定性。",
    }
