"""三维推荐位置规则。

该模块把 posterior peak、posterior mean 和高概率区域合并成稳定的推荐表达。
推荐结果仍是科研候选，不是工程确诊。
"""

from __future__ import annotations

from typing import Any

import numpy as np


def build_posterior_recommendation(posterior_summary: dict[str, Any], uncertainty_summary: dict[str, Any]) -> dict[str, Any]:
    """根据 posterior-like 诊断给出推荐位置类型和 warning。"""

    peak = posterior_summary["posterior_peak_location"]
    mean = posterior_summary["posterior_mean_location"]
    peak_vec = np.array([peak["x_m"], peak["y_m"], peak["depth_m"]], dtype=float)
    mean_vec = np.array([mean["x_m"], mean["y_m"], mean["depth_m"]], dtype=float)
    peak_mean_distance = float(np.linalg.norm(peak_vec - mean_vec))
    multi_peak = bool(uncertainty_summary.get("multi_peak_warning", False))
    ambiguous = bool(uncertainty_summary.get("ambiguity_warning", False))
    if multi_peak:
        recommended_type = "multi_peak_posterior_region"
    elif ambiguous:
        recommended_type = "posterior_peak_with_wide_uncertainty"
    else:
        recommended_type = "posterior_peak"
    return {
        "posterior_recommended_location": peak,
        "posterior_mean_location": mean,
        "posterior_peak_mean_distance_m": peak_mean_distance,
        "recommended_location_type": recommended_type,
        "ambiguity_warning": ambiguous,
        "multi_peak_warning": multi_peak,
        "note": "posterior-like recommendation for research candidate only",
    }
