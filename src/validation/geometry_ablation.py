"""三维观测几何消融实验。

目的不是实现真实野外采集设计，而是在同一运动学正演框架下比较不同
source_xyz / receiver_xyz 覆盖方式对 y/depth 不确定性的影响。
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from src.features.direct_arrival import predict_direct_arrival_times
from src.features.direct_wave_mute import mute_direct_wave
from src.forward.multishot_forward import synthesize_multishot_forward
from src.localization.multishot_scan import run_multishot_scan
from src.preprocessing.preprocessing_pipeline import run_preprocessing_pipeline
from src.validation.common import clone_params, make_diagnostic_scan_grid, summarize_volume


def _geometry_cases(params: SimpleNamespace, source_xyz: np.ndarray, receiver_xyz: np.ndarray) -> dict[str, dict[str, np.ndarray]]:
    """生成四类轻量三维几何案例。"""

    width = float(params.road.width_m)
    cases: dict[str, dict[str, np.ndarray]] = {}
    cases["geometry_case_A_single_side_line"] = {
        "source_xyz": source_xyz.copy(),
        "receiver_xyz": receiver_xyz.copy(),
    }

    non_collinear = source_xyz.copy()
    offsets = np.linspace(-0.22 * width, 0.22 * width, len(non_collinear))
    non_collinear[:, 1] = np.clip(non_collinear[:, 1] + offsets, 0.0, width)
    cases["geometry_case_B_non_collinear_sources"] = {
        "source_xyz": non_collinear,
        "receiver_xyz": receiver_xyz.copy(),
    }

    two_side = source_xyz.copy()
    two_side[::2, 1] = 0.0
    two_side[1::2, 1] = width
    cases["geometry_case_C_two_side_sources"] = {
        "source_xyz": two_side,
        "receiver_xyz": receiver_xyz.copy(),
    }

    poly_receiver = receiver_xyz.copy()
    if len(poly_receiver) > 1:
        phase = np.linspace(0.0, 2.0 * np.pi, len(poly_receiver))
        poly_receiver[:, 1] = np.clip(params.fiber.y_m + 0.08 * width * np.sin(phase), 0.0, width)
    cases["geometry_case_D_polyline_receiver"] = {
        "source_xyz": source_xyz.copy(),
        "receiver_xyz": poly_receiver,
    }
    return cases


def run_geometry_ablation(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
    velocity_model: Any,
) -> dict[str, Any]:
    """运行小规模三维几何消融。

    每个案例都会重新合成 DAS-like 运动学数据，然后在三维诊断网格上扫描。
    这样比只拿同一数据更换几何走时更自洽，但仍然是轻量科研原型，不是
    大规模 survey 设计优化。
    """

    trial = clone_params(params)
    trial.scan.score_mode = "energy"
    trial.scan.score_method = "diffraction_energy_stack"
    trial.scan.active_score_kind = "unweighted"
    scan_grid = make_diagnostic_scan_grid(params)
    cases = _geometry_cases(params, source_xyz, receiver_xyz)
    results: dict[str, Any] = {}

    for case_name, geometry in cases.items():
        simulated = synthesize_multishot_forward(
            trial,
            geometry["source_xyz"],
            geometry["receiver_xyz"],
            scatter_xyz,
            scatter_weight,
            velocity_model,
        )["synthetic_data"]
        processed, preprocessing_info = run_preprocessing_pipeline(simulated, trial)
        direct_times = predict_direct_arrival_times(trial, geometry["source_xyz"], geometry["receiver_xyz"], velocity_model)
        scan_data = mute_direct_wave(
            processed,
            params.derived.time_axis,
            direct_times,
            params.scan.direct_mute_half_width_s,
            mode=params.scan.direct_mute_mode,
        )
        scan_result = run_multishot_scan(
            scan_data,
            params.derived.time_axis,
            geometry["source_xyz"],
            geometry["receiver_xyz"],
            velocity_model,
            scan_grid,
            trial,
        )
        summary = summarize_volume(trial, scan_result["score_volume_unweighted"], scan_grid)
        results[case_name] = {
            "best_location": summary["best_location"],
            "truth_error": summary["truth_error"],
            "x_span_m": summary["x_span_m"],
            "y_span_m": summary["y_span_m"],
            "depth_span_m": summary["depth_span_m"],
            "high_score_region_point_count": summary["high_score_region_point_count"],
            "high_score_component_count": summary["high_score_component_count"],
            "multi_region_warning": summary["multi_region_warning"],
            "preprocessing_info": preprocessing_info,
            "source_y_span_m": float(np.max(geometry["source_xyz"][:, 1]) - np.min(geometry["source_xyz"][:, 1])),
            "receiver_y_span_m": float(np.max(geometry["receiver_xyz"][:, 1]) - np.min(geometry["receiver_xyz"][:, 1])),
            "low_confidence_flag": "low"
            if summary["y_span_m"] >= params.confidence.coupling_warning_span_y_m
            or summary["depth_span_m"] >= params.confidence.coupling_warning_span_depth_m
            else "medium",
        }

    best_y = min(results, key=lambda name: results[name]["y_span_m"])
    best_depth = min(results, key=lambda name: results[name]["depth_span_m"])
    best_error = min(results, key=lambda name: results[name]["truth_error"]["distance_m"])
    return {
        "cases": results,
        "best_y_resolution_case": best_y,
        "best_depth_stability_case": best_depth,
        "best_truth_error_case": best_error,
        "scan_grid_shape": (
            len(scan_grid["x_grid"]),
            len(scan_grid["y_grid"]),
            len(scan_grid["depth_grid"]),
        ),
        "note": "几何消融基于重新合成的运动学数据和轻量三维诊断网格。",
    }

