"""Stage 4B 验证报告生成。"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _location_text(item: dict[str, Any]) -> str:
    loc = item.get("best_location") or item.get("recommended_location") or {}
    err = item.get("truth_error", {})
    return (
        f"x={loc.get('x_m')}, y={loc.get('y_m')}, h={loc.get('depth_m')}, "
        f"error={err.get('distance_m')}"
    )


def write_preprocessing_ablation_report(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# 预处理消融验证报告",
        "",
        "本报告比较不同预处理组合对三维运动学扫描的影响。消融使用轻量三维诊断网格，不是大规模鲁棒性扫描。",
        "",
        "| case | best | y_span_m | depth_span_m | diffraction_ratio | direct_residual | flag |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for name, item in result["cases"].items():
        lines.append(
            "| "
            f"{name} | {_location_text(item)} | {item['y_span_m']:.4g} | {item['depth_span_m']:.4g} | "
            f"{item['diffraction_curve_energy_ratio']:.4g} | {item['direct_wave_residual_ratio']:.4g} | "
            f"{item['low_confidence_flag']} |"
        )
    lines.extend(
        [
            "",
            "## 结论",
            "",
            f"- 最小真值误差组合：`{result['best_truth_error_case']}`。",
            f"- y/depth 跨度最小组合：`{result['narrowest_y_depth_case']}`。",
            "- 若某组合降低 direct_residual 但同时降低 diffraction_ratio，应视为可能误伤有效绕射。",
            "- 当前仍是 kinematic approximation 与 DAS-like response approximation，不能作为工程确诊。",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_fk_filter_validation_report(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# FK / f-v 滤波验证报告",
        "",
        "当前 FK 滤波是简化速度扇区 QC，不是成熟面波 FK 分离软件。",
        "",
        f"- strict FK applicable: `{result['applicable_as_strict_fk']}`",
        f"- warning: {result.get('warning') or '无'}",
        f"- direct wave reduction ratio: `{result['direct_wave_reduction_ratio']:.4g}`",
        f"- diffraction preservation ratio: `{result['diffraction_preservation_ratio']:.4g}`",
        f"- shape preserved: `{result['shape_preserved']}`",
        "",
        "## 解释",
        "",
        "- direct wave reduction ratio 越高，说明直达波局部能量削弱越明显。",
        "- diffraction preservation ratio 接近或大于 1，说明理论绕射曲线附近能量没有被明显误伤。",
        "- receiver 不是 straight 或通道非均匀时，f-k 解释只能作为近似 QC。",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_attribute_validation_report(path: Path, title: str, summary: dict[str, Any], note: str) -> None:
    lines = [
        f"# {title}",
        "",
        f"- best: {_location_text(summary)}",
        f"- y_span_m: `{summary.get('y_span_m')}`",
        f"- depth_span_m: `{summary.get('depth_span_m')}`",
        f"- high_score_component_count: `{summary.get('high_score_component_count')}`",
        f"- multi_region_warning: `{summary.get('multi_region_warning')}`",
        "",
        note,
        "",
        "该属性仍是运动学 DAS-like 数据上的科研诊断，不是工程确诊。",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_multi_attribute_ablation_report(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# 多属性评分消融报告",
        "",
        "| group | best | y_span_m | depth_span_m | components | flag |",
        "|---|---|---:|---:|---:|---|",
    ]
    for name, item in result["groups"].items():
        lines.append(
            "| "
            f"{name} | {_location_text(item)} | {item['y_span_m']:.4g} | {item['depth_span_m']:.4g} | "
            f"{item['high_score_component_count']} | {item['low_confidence_flag']} |"
        )
    lines.extend(
        [
            "",
            f"- best_group_by_truth_error: `{result.get('best_group_by_truth_error')}`",
            f"- full_multi_attribute_improved_over_energy: `{result.get('multi_attribute_improved_over_energy')}`",
            "",
            result.get("note", ""),
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_geometry_ablation_report(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# 三维几何消融报告",
        "",
        "每个案例都重新合成运动学 DAS-like 数据，并在三维诊断网格上扫描。",
        "",
        "| geometry case | best | y_span_m | depth_span_m | source_y_span_m | receiver_y_span_m | flag |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for name, item in result["cases"].items():
        lines.append(
            "| "
            f"{name} | {_location_text(item)} | {item['y_span_m']:.4g} | {item['depth_span_m']:.4g} | "
            f"{item['source_y_span_m']:.4g} | {item['receiver_y_span_m']:.4g} | {item['low_confidence_flag']} |"
        )
    lines.extend(
        [
            "",
            f"- y 方向跨度改善最明显：`{result['best_y_resolution_case']}`。",
            f"- depth 稳定性最好：`{result['best_depth_stability_case']}`。",
            f"- 真值误差最小：`{result['best_truth_error_case']}`。",
            "",
            "若非共线或双侧震源明显缩小 y/depth 跨度，说明当前场景更应优先增加震源方位覆盖，而不是只调 score。",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")

