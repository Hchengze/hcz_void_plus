"""基础置信度指标汇总与报告输出。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np

from src.confidence.consistency import compute_multishot_consistency
from src.confidence.coupling_warning import analyze_stage3b_scan_warnings, analyze_y_depth_coupling, assign_confidence_flag
from src.confidence.peak_analysis import analyze_peak_sharpness, compute_score_contrast
from src.confidence.uncertainty_region import build_recommended_location, compute_3d_high_score_region
from src.model.velocity_model import UniformVelocityModel


def build_confidence_metrics(
    params: SimpleNamespace,
    scan_result: dict[str, Any],
    scan_data: np.ndarray,
    time_axis: np.ndarray,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    velocity_model: UniformVelocityModel,
) -> dict[str, Any]:
    """汇总 Stage 3 基础置信度诊断指标。

    输入：
        scan_result 来自基础 x-y-h 多炮扫描；scan_data 是直达波 mute 后用于扫描的
        DAS-like 数据，shape = shot × time × channel。

    输出：
        可 JSON 保存的 dict。所有指标都用于人工判断扫描结果稳定性，不代表工程确诊。
    """

    score_volume = scan_result["score_volume"]
    best_index = tuple(int(v) for v in scan_result["best_index"])
    peak = analyze_peak_sharpness(score_volume, best_index, params.confidence.neighborhood_radius)
    contrast = compute_score_contrast(score_volume, peak["best_score"])
    consistency = compute_multishot_consistency(
        scan_data,
        time_axis,
        source_xyz,
        receiver_xyz,
        velocity_model,
        scan_result["best_location"],
        params,
    )
    coupling = analyze_y_depth_coupling(
        score_volume,
        params.derived.scan_x_grid,
        params.derived.scan_y_grid,
        params.derived.scan_depth_grid,
        best_index,
        params,
    )
    stage3b_warnings = analyze_stage3b_scan_warnings(
        score_volume,
        params.derived.scan_y_grid,
        params.derived.scan_depth_grid,
        best_index,
        scan_result,
        params,
    )
    high_score_region = compute_3d_high_score_region(
        score_volume,
        params.derived.scan_x_grid,
        params.derived.scan_y_grid,
        params.derived.scan_depth_grid,
        params.confidence.threshold_ratio,
    )
    flag = assign_confidence_flag(
        peak["peak_sharpness"],
        contrast["score_contrast"],
        consistency["coefficient_of_variation"],
        consistency["warning"],
        coupling["warning"],
        stage3b_warnings,
        params,
        high_score_region,
    )
    recommendation = build_recommended_location(params, scan_result, stage3b_warnings, high_score_region)
    return {
        "peak": peak,
        "contrast": contrast,
        "multi_shot_consistency": consistency,
        "y_depth_coupling": coupling,
        "stage3b_warnings": stage3b_warnings,
        "high_score_region": high_score_region,
        "recommendation": recommendation,
        "recommended_location": recommendation["recommended_location"],
        "recommended_location_type": recommendation["recommended_location_type"],
        "recommended_location_reason": recommendation["recommended_location_reason"],
        "depth_uncertainty_interval_m": recommendation["depth_uncertainty_interval_m"],
        "unweighted_best_location": scan_result.get("unweighted_best_location"),
        "raw_best_location": scan_result.get("raw_best_location"),
        "weighted_best_location": scan_result.get("weighted_best_location"),
        "raw_weighted_difference": scan_result.get("raw_weighted_difference"),
        "low_confidence_flag": flag,
        "note": "规则型基础置信度诊断；不是概率置信度、不是工程确诊。",
    }


def write_confidence_report(params: SimpleNamespace, output_path: Path, metrics: dict[str, Any]) -> None:
    """写出中文基础置信度报告。"""

    peak = metrics["peak"]
    contrast = metrics["contrast"]
    consistency = metrics["multi_shot_consistency"]
    coupling = metrics["y_depth_coupling"]
    stage3b = metrics["stage3b_warnings"]
    unweighted_best = metrics.get("unweighted_best_location") or metrics.get("raw_best_location") or {}
    weighted_best = metrics.get("weighted_best_location") or {}
    diff = metrics.get("raw_weighted_difference") or {}
    high_region = metrics["high_score_region"]
    recommendation = metrics["recommendation"]
    content = f"""# 基础置信度诊断报告

## 指标摘要

- peak sharpness：`{peak["peak_sharpness"]:.4g}`
- local background mean：`{peak["local_background_mean"]:.4g}`
- score contrast：`{contrast["score_contrast"]:.4g}`
- score percentile：`{contrast["score_percentile"]:.2f}%`
- multi-shot consistency mean：`{consistency["mean"]:.4g}`
- multi-shot consistency std：`{consistency["std"]:.4g}`
- multi-shot consistency CV：`{consistency["coefficient_of_variation"]:.4g}`
- y-depth coupling warning：`{coupling["warning"]}`
- best depth at boundary warning：`{stage3b["best_depth_at_boundary_warning"]}`
- wide y high-score zone warning：`{stage3b["wide_y_high_score_zone_warning"]}`
- raw/weighted divergence warning：`{stage3b["raw_weighted_divergence_warning"]}`
- shallow bias warning：`{stage3b["shallow_bias_warning"]}`
- confidence flag：`{metrics["low_confidence_flag"]}`

## unweighted 与 weighted best 对比

- unweighted_best：x=`{unweighted_best.get("x_m")}` m，y=`{unweighted_best.get("y_m")}` m，h=`{unweighted_best.get("depth_m")}` m
- weighted_best：x=`{weighted_best.get("x_m")}` m，y=`{weighted_best.get("y_m")}` m，h=`{weighted_best.get("depth_m")}` m
- unweighted -> weighted 差异：dx=`{diff.get("dx_m")}` m，dy=`{diff.get("dy_m")}` m，dh=`{diff.get("ddepth_m")}` m，三维距离=`{diff.get("distance_m")}` m

## 推荐位置表达

- recommended_location_type：`{recommendation["recommended_location_type"]}`
- recommended_location：`{recommendation["recommended_location"]}`
- depth uncertainty interval：`{recommendation["depth_uncertainty_interval_m"]}` m
- recommended reason：{recommendation["recommended_location_reason"]}

## 三维高分区统计

- high score threshold：`{high_region["threshold_ratio"]}` × best_score
- high score point count：`{high_region["high_score_region_point_count"]}`
- high score component count：`{high_region.get("high_score_component_count")}`
- multi region warning：`{high_region.get("multi_region_warning")}`
- x span：`{high_region["x_span_m"]}` m
- y span：`{high_region["y_span_m"]}` m
- depth span：`{high_region["depth_span_m"]}` m
- equivalent uncertainty box：`{high_region["equivalent_uncertainty_box"]}`

## Stage 3B 新增 warning

- best depth 位于扫描边界：`{stage3b["best_depth_at_boundary_warning"]}`
- best_x 高分区 y 跨度：`{stage3b["wide_y_high_score_span_m"]}` m
- raw/weighted 位置分歧：`{stage3b["raw_weighted_divergence_warning"]}`
- 深度先验偏置：`{stage3b["depth_prior_bias_warning"]}`
- weighted 浅部偏置：`{stage3b["shallow_bias_warning"]}`
- 诊断文字：{"；".join(stage3b["messages"])}

## y-depth 耦合检查

- best_x：`{coupling["best_x_m"]}` m
- 高分阈值：`{coupling["threshold_ratio"]}` × best_score
- 高分点数量：`{coupling["high_score_point_count"]}`
- y 跨度：`{coupling["y_span_m"]}` m
- depth 跨度：`{coupling["depth_span_m"]}` m
- 诊断：{coupling["message"]}

## 解释边界

这些指标只用于 Stage 3B 科研原型的结果自检。它们能够提示峰值是否集中、多炮贡献是否均衡、深度是否贴边、raw/weighted 是否分歧，以及单侧 DAS-like 几何下是否存在 y-depth 或宽 y 高分区风险，但不能替代完整置信度体系，也不能作为工程确诊结论。
"""
    output_path.write_text(content, encoding="utf-8")
