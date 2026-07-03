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


def write_velocity_model_ablation_report(path: Path, result: dict[str, Any]) -> None:
    """写出速度模型消融报告。

    报告重点不是宣布某个模型“真实”，而是说明分层/非均匀运动学速度如何改变
    绕射走时、定位误差和三维高分区跨度。
    """

    lines = [
        "# 速度模型消融报告",
        "",
        "本报告比较 uniform、layered、lateral gradient、localized low velocity zone 等等效 Rayleigh 速度模型。",
        "所有结果仍是 straight-ray kinematic approximation，不是 3D elastic wavefield。",
        "",
        "| velocity model | best | error_m | y_span_m | depth_span_m | residual_rms_ms | flag |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for name, item in result["cases"].items():
        lines.append(
            "| "
            f"{name} | {_location_text(item)} | {item['truth_error']['distance_m']:.4g} | "
            f"{item['y_span_m']:.4g} | {item['depth_span_m']:.4g} | "
            f"{1000.0 * item['travel_time_residual_to_uniform_rms_s']:.4g} | {item['confidence_flag']} |"
        )
    lines.extend(
        [
            "",
            "## 结论",
            "",
            f"- 真值误差最小模型：`{result['best_truth_error_case']}`。",
            f"- 深度误差最小模型：`{result['best_depth_case']}`。",
            f"- 相对 uniform 走时残差最大模型：`{result['largest_travel_time_residual_case']}`。",
            "- 如果 layered 与 uniform 的走时残差不可忽略，真实数据反演不应继续只依赖 uniform 速度。",
            "- 局部低速带可能导致定位偏移，也可能被误解释为空洞响应，因此必须在报告中作为风险列出。",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_model_mismatch_report(path: Path, result: dict[str, Any]) -> None:
    """写出正演/扫描速度模型错配报告。"""

    lines = [
        "# 正演模型与扫描模型错配报告",
        "",
        "真实道路介质与反演速度假设通常不一致。本报告用轻量三维运动学实验检查这种错配对定位的影响。",
        "",
        "| case | forward model | scan model | best | error_m | y_span_m | depth_span_m | flag |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for name, item in result["cases"].items():
        lines.append(
            "| "
            f"{name} | {item['forward_model_type']} | {item['scan_model_type']} | {_location_text(item)} | "
            f"{item['truth_error']['distance_m']:.4g} | {item['y_span_m']:.4g} | "
            f"{item['depth_span_m']:.4g} | {item['low_confidence_flag']} |"
        )
    lines.extend(
        [
            "",
            "## 风险解释",
            "",
            f"- 误差最小案例：`{result['safest_case']}`。",
            f"- 误差最大案例：`{result['riskiest_case']}`。",
            f"- 当前最低推荐速度模型：`{result['minimum_recommended_velocity_model']}`。",
            "- 如果真实为 layered 但扫描仍用 uniform，depth 与 y-depth 耦合可能出现系统偏差。",
            "- 本报告只用于科研算法风险诊断，不能作为工程确诊或速度结构反演结论。",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_forward_engine_ablation_report(path: Path, result: dict[str, Any]) -> None:
    """写出 Stage 5B 正演引擎消融报告。

    报告强调 F0/F1/F2 的角色差异：F1 是当前主定位 forward，F2 只验证声学
    波动方程基础设施，不能被解释为 Rayleigh 波或空洞弹性散射正演。
    """

    layered_vs_baseline = result["layered_vs_baseline"]
    lines = [
        "# 正演引擎消融报告",
        "",
        "本报告比较 `kinematic_baseline`、`layered_kinematic` 与 `acoustic2d_prototype` 的阶段角色。",
        "`acoustic2d_prototype` 只验证波动方程数值框架，不参与 DAS-like 主定位，也不能代表 Rayleigh 波正演。",
        "",
        "| engine | stage | velocity/model | data/snapshot shape | RMS or max amplitude | role |",
        "|---|---|---|---|---:|---|",
    ]
    baseline = result["engines"]["kinematic_baseline"]
    layered = result["engines"]["layered_kinematic"]
    acoustic = result["engines"]["acoustic2d_prototype"]
    lines.extend(
        [
            "| "
            f"kinematic_baseline | {baseline['forward_stage']} | {baseline['velocity_model_type']} | "
            f"{baseline['data_shape']} | {baseline['synthetic_rms']:.4g} | F0 快速基线 |",
            "| "
            f"layered_kinematic | {layered['forward_stage']} | {layered['velocity_model_type']} | "
            f"{layered['data_shape']} | {layered['synthetic_rms']:.4g} | F1 当前主线 |",
            "| "
            f"acoustic2d_prototype | {acoustic['forward_stage']} | scalar acoustic | "
            f"{acoustic['shot_gather_shape']} / {acoustic['wavefield_snapshot_shape']} | "
            f"{acoustic['max_abs_amplitude']:.4g} | F2 validation prototype |",
        ]
    )
    lines.extend(
        [
            "",
            "## F1 相对 F0 的差异",
            "",
            f"- synthetic RMS difference：`{layered_vs_baseline['synthetic_rms_difference']:.4g}`。",
            f"- synthetic relative difference：`{layered_vs_baseline['synthetic_relative_difference']:.4g}`。",
            f"- travel-time residual mean：`{layered_vs_baseline['travel_time_residual_mean_ms']:.4g}` ms。",
            f"- travel-time residual RMS：`{layered_vs_baseline['travel_time_residual_rms_ms']:.4g}` ms。",
            f"- travel-time residual max abs：`{layered_vs_baseline['travel_time_residual_max_abs_ms']:.4g}` ms。",
            "",
            "## acoustic2d prototype 边界",
            "",
            f"- CFL stable：`{acoustic['cfl_stable']}`。",
            f"- CFL number：`{acoustic['cfl_number']:.4g}`。",
            "- acoustic2d 只有标量声学压力场，没有剪切波和自由表面 Rayleigh 模式。",
            "- acoustic2d 可以验证网格、震源、接收、absorbing boundary、CFL 和快照输出。",
            "- acoustic2d 不能验证 Rayleigh/free-surface/void scattering；下一步必须进入 elastic2d。",
            "",
            "## 当前结论",
            "",
            "- active forward engine：`layered_kinematic`。",
            "- available forward engines：`kinematic_baseline, layered_kinematic, acoustic2d_prototype`。",
            "- next required forward：`elastic2d`。",
            "- 当前结果仍是科研候选区，不是工程确诊。",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_acoustic2d_prototype_report(path: Path, result: dict[str, Any]) -> None:
    """写出 acoustic2d prototype 专项报告。"""

    acoustic = result["engines"]["acoustic2d_prototype"]
    lines = [
        "# acoustic2d prototype 验证报告",
        "",
        "`acoustic2d_prototype` 是二维标量 acoustic FDTD 最小原型。它只用于验证波动方程基础设施，不能代表 Rayleigh 波、自由表面或空洞弹性散射正演。",
        "",
        "## 输出",
        "",
        f"- shot gather shape：`{acoustic['shot_gather_shape']}`。",
        f"- wavefield snapshot shape：`{acoustic['wavefield_snapshot_shape']}`。",
        f"- snapshot count：`{acoustic['snapshot_count']}`。",
        f"- CFL stable：`{acoustic['cfl_stable']}`。",
        f"- CFL number：`{acoustic['cfl_number']:.4g}`。",
        f"- max abs amplitude：`{acoustic['max_abs_amplitude']:.4g}`。",
        f"- energy：`{acoustic['energy']:.4g}`。",
        "",
        "## 能验证什么",
        "",
        "- 二维网格和分层 acoustic velocity 的组织方式。",
        "- Ricker 震源、接收线和 shot gather 输出。",
        "- sponge absorbing boundary 与 CFL 稳定性检查。",
        "- wavefield snapshots 的保存和可视化链路。",
        "",
        "## 不能验证什么",
        "",
        "- 不能验证 Rayleigh 波。",
        "- 不能验证自由表面条件。",
        "- 不能验证 void/free-surface/elastic scattering。",
        "- 不能替代 `layered_kinematic` 主流程，也不能替代下一步 `elastic2d`。",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
