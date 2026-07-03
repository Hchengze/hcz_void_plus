"""基础置信度指标汇总与报告输出。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np

from src.confidence.consistency import compute_multishot_consistency
from src.confidence.coupling_warning import analyze_y_depth_coupling, assign_confidence_flag
from src.confidence.peak_analysis import analyze_peak_sharpness, compute_score_contrast
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
    flag = assign_confidence_flag(
        peak["peak_sharpness"],
        contrast["score_contrast"],
        consistency["coefficient_of_variation"],
        consistency["warning"],
        coupling["warning"],
        params,
    )
    return {
        "peak": peak,
        "contrast": contrast,
        "multi_shot_consistency": consistency,
        "y_depth_coupling": coupling,
        "low_confidence_flag": flag,
        "note": "规则型基础置信度诊断；不是概率置信度、不是工程确诊。",
    }


def write_confidence_report(params: SimpleNamespace, output_path: Path, metrics: dict[str, Any]) -> None:
    """写出中文基础置信度报告。"""

    peak = metrics["peak"]
    contrast = metrics["contrast"]
    consistency = metrics["multi_shot_consistency"]
    coupling = metrics["y_depth_coupling"]
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
- confidence flag：`{metrics["low_confidence_flag"]}`

## y-depth 耦合检查

- best_x：`{coupling["best_x_m"]}` m
- 高分阈值：`{coupling["threshold_ratio"]}` × best_score
- 高分点数量：`{coupling["high_score_point_count"]}`
- y 跨度：`{coupling["y_span_m"]}` m
- depth 跨度：`{coupling["depth_span_m"]}` m
- 诊断：{coupling["message"]}

## 解释边界

这些指标只用于 Stage 3 科研原型的结果自检。它们能够提示峰值是否集中、多炮贡献是否均衡、单侧 DAS-like 几何下是否存在 y-depth 耦合风险，但不能替代完整置信度体系，也不能作为工程确诊结论。
"""
    output_path.write_text(content, encoding="utf-8")

