"""多属性评分消融验证。"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from src.validation.common import normalize_volume, summarize_volume


ATTRIBUTE_GROUPS: dict[str, dict[str, float]] = {
    "energy_only": {"energy_score": 1.0},
    "normalized_energy_only": {"normalized_energy_score": 1.0},
    "matched_wavelet_only": {"matched_wavelet_score": 1.0},
    "semblance_only": {"semblance_score": 1.0},
    "energy_matched_wavelet": {"energy_score": 1.0, "matched_wavelet_score": 1.0},
    "energy_matched_wavelet_semblance": {
        "energy_score": 1.0,
        "matched_wavelet_score": 1.0,
        "semblance_score": 0.5,
    },
    "full_multi_attribute": {
        "energy_score": 1.0,
        "normalized_energy_score": 0.5,
        "matched_wavelet_score": 1.0,
        "semblance_score": 0.5,
        "frequency_shift_score": 0.0,
    },
}


def _combine_group(attribute_volumes: dict[str, np.ndarray], weights: dict[str, float]) -> np.ndarray:
    """把若干属性体归一化后加权组合。"""

    total_weight = sum(weight for weight in weights.values() if weight > 0)
    if total_weight <= 0:
        return normalize_volume(attribute_volumes["energy_score"])
    combined = None
    for name, weight in weights.items():
        if weight <= 0:
            continue
        volume = normalize_volume(attribute_volumes[name])
        combined = volume * weight if combined is None else combined + volume * weight
    return combined / max(total_weight, 1.0e-12)


def run_multi_attribute_ablation(params: SimpleNamespace, scan_result: dict[str, Any]) -> dict[str, Any]:
    """比较不同属性组合是否优于 energy only。

    本函数复用主扫描已经计算出的 attribute score volumes，不重复扫描，因此
    可以快速回答“multi_attribute 是否真的改善定位或收窄 y/depth 不确定性”。
    """

    attribute_volumes = scan_result.get("attribute_score_volumes", {})
    groups: dict[str, Any] = {}
    volumes: dict[str, np.ndarray] = {}
    for group_name, weights in ATTRIBUTE_GROUPS.items():
        missing = [name for name in weights if name not in attribute_volumes]
        if missing:
            continue
        volume = _combine_group(attribute_volumes, weights)
        volumes[group_name] = volume
        summary = summarize_volume(params, volume)
        groups[group_name] = {
            "weights": weights,
            "best_location": summary["best_location"],
            "truth_error": summary["truth_error"],
            "x_span_m": summary["x_span_m"],
            "y_span_m": summary["y_span_m"],
            "depth_span_m": summary["depth_span_m"],
            "high_score_component_count": summary["high_score_component_count"],
            "multi_region_warning": summary["multi_region_warning"],
            "low_confidence_flag": "low"
            if summary["y_span_m"] >= params.confidence.coupling_warning_span_y_m
            or summary["depth_span_m"] >= params.confidence.coupling_warning_span_depth_m
            else "medium",
        }
    energy_error = groups.get("energy_only", {}).get("truth_error", {}).get("distance_m")
    best_group = min(groups, key=lambda name: groups[name]["truth_error"]["distance_m"]) if groups else None
    full_error = groups.get("full_multi_attribute", {}).get("truth_error", {}).get("distance_m")
    improved_over_energy = bool(
        energy_error is not None and full_error is not None and full_error < energy_error
    )
    return {
        "groups": groups,
        "volumes": volumes,
        "best_group_by_truth_error": best_group,
        "multi_attribute_improved_over_energy": improved_over_energy,
        "note": (
            "若 full_multi_attribute 未优于 energy_only，应在报告中诚实说明当前多属性框架尚未证明优于 energy stack。"
        ),
    }

