"""三维不确定性体与高概率区域诊断。

这里的不确定性来自三维 posterior-like 体和 high-score/high-probability 区域，
用于辅助人工判断 x/y/depth 的模糊性。它不是严格概率置信区间，也不是工程风险边界。
"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.localization.connected_components_3d import label_probability_components


def high_probability_region(
    posterior_volume: np.ndarray,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    depth_grid: np.ndarray,
    mass_threshold: float = 0.9,
) -> dict[str, Any]:
    """按累计概率质量提取高概率候选区域。

    做法是按 posterior-like 权重从高到低排序，取累计质量达到 ``mass_threshold`` 的点。
    这比固定 score 阈值更适合表达“当前反演诊断主要支持哪些候选体”。
    """

    posterior = np.asarray(posterior_volume, dtype=float)
    flat = posterior.ravel()
    if flat.size == 0:
        raise ValueError("posterior_volume 不能为空")
    total = float(np.sum(flat))
    if total <= 0:
        weights = np.full_like(flat, 1.0 / flat.size, dtype=float)
    else:
        weights = flat / total
    order = np.argsort(weights)[::-1]
    cumulative = np.cumsum(weights[order])
    keep_count = int(np.searchsorted(cumulative, mass_threshold, side="left") + 1)
    keep_count = max(1, min(keep_count, flat.size))
    mask_flat = np.zeros_like(weights, dtype=bool)
    mask_flat[order[:keep_count]] = True
    mask = mask_flat.reshape(posterior.shape)

    indices = np.argwhere(mask)
    xs = np.asarray(x_grid)[indices[:, 0]]
    ys = np.asarray(y_grid)[indices[:, 1]]
    zs = np.asarray(depth_grid)[indices[:, 2]]
    components = label_probability_components(mask, x_grid, y_grid, depth_grid)
    return {
        "mass_threshold": float(mass_threshold),
        "probability_mass": float(np.sum(weights[mask_flat])),
        "point_count": int(indices.shape[0]),
        "x_span_m": float(np.max(xs) - np.min(xs)) if indices.size else 0.0,
        "y_span_m": float(np.max(ys) - np.min(ys)) if indices.size else 0.0,
        "depth_span_m": float(np.max(zs) - np.min(zs)) if indices.size else 0.0,
        "mask": mask,
        "connected_components_3d": components,
        "multi_peak_warning": bool(components.get("component_count", 0) > 1),
    }


def summarize_uncertainty_volume(
    posterior_summary: dict[str, Any],
    high_region: dict[str, Any],
    *,
    y_depth_span_ratio_warning: float = 1.5,
) -> dict[str, Any]:
    """汇总 posterior-like 不确定性、连通体和 y-depth 耦合 warning。"""

    axes = np.asarray(posterior_summary.get("uncertainty_ellipsoid_axes", [0.0, 0.0, 0.0]), dtype=float)
    y_span = float(high_region.get("y_span_m", 0.0))
    depth_span = float(high_region.get("depth_span_m", 0.0))
    y_depth_coupling_warning = y_span > 0.0 and depth_span > 0.0 and max(y_span, depth_span) / max(min(y_span, depth_span), 1.0e-9) < y_depth_span_ratio_warning
    ambiguity_warning = bool(high_region.get("multi_peak_warning", False) or axes[0] > max(axes[-1], 1.0e-9) * 4.0)
    return {
        "posterior_peak_location": posterior_summary.get("posterior_peak_location"),
        "posterior_mean_location": posterior_summary.get("posterior_mean_location"),
        "posterior_covariance_3x3": posterior_summary.get("posterior_covariance_3x3"),
        "uncertainty_ellipsoid_axes": axes,
        "high_probability_region": {
            key: value for key, value in high_region.items() if key != "mask"
        },
        "connected_components_3d": high_region.get("connected_components_3d"),
        "recommended_location_type": "posterior_peak_with_uncertainty_region",
        "ambiguity_warning": ambiguity_warning,
        "y_depth_coupling_warning": bool(y_depth_coupling_warning),
        "multi_peak_warning": bool(high_region.get("multi_peak_warning", False)),
        "uncertainty_note": "rule-based/posterior-like uncertainty, not strict probability inversion",
    }
