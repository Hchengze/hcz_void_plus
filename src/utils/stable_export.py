"""导出 outputs/latest_stable 精选稳定成果。"""

from __future__ import annotations

import shutil
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.utils.latest_stable_manifest import (
    STAGE5E_FIGURE_SPECS,
    build_figure_metadata,
    specs_by_category,
)
from src.validation.figure_self_check import run_figure_self_check, write_figure_self_check_report
from src.validation.repository_health import build_repository_health_report, write_repository_health_report
from src.validation.scientific_figure_self_check import (
    run_scientific_figure_self_check,
    write_scientific_figure_self_check_report,
)


CURATED_FIGURES = specs_by_category()

CURATED_REPORTS = {
    "core": [
        "report_full_pipeline.md",
        "report_confidence.md",
        "report_repository_health.md",
        "report_figure_self_check.md",
        "report_scientific_figure_self_check.md",
    ],
    "forward": [
        "report_forward_engine_ablation.md",
        "report_acoustic2d_prototype.md",
        "report_elastic2d_rayleigh_validation.md",
        "report_elastic2d_void_scattering.md",
        "report_elastic2d_das_response.md",
        "report_elastic_vs_kinematic.md",
        "report_elastic2d_numerical_sensitivity.md",
    ],
    "localization": [
        "report_multi_attribute_ablation.md",
        "report_geometry_ablation.md",
    ],
    "uncertainty": [],
    "diagnostics": [
        "report_velocity_model_ablation.md",
        "report_model_mismatch.md",
        "report_velocity_model_audit.md",
        "report_velocity_model_visualization.md",
        "report_velocity_model_physics_bridge.md",
    ],
}

LEGACY_STABLE_FILES = [
    "旧 Stage 3/4/5A 的大量诊断图件不再平铺保存在 latest_stable/figures 根目录。",
    "FK、matched wavelet、semblance、frequency shift 等详细验证仍保存在时间戳运行目录。",
    "latest_stable 只保留当前阶段最关键 curated outputs。",
]


def get_git_commit_id(repo_root: Path) -> str:
    """读取当前 Git HEAD 短哈希；失败时返回 unknown。

    latest_stable 的 summary 需要记录“本轮对应 commit id”。在尚未 commit 的运行中，
    该值表示运行时的当前 HEAD；最终提交哈希仍以 git log / 最终回复为准。
    """

    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            check=True,
            text=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return completed.stdout.strip() or "unknown"


def _reset_latest_stable_dir(latest_stable_dir: Path, output_root_dir: Path) -> None:
    """安全清理 latest_stable 目录。

    该函数会解析绝对路径，确认 latest_stable 位于 output_root_dir 内部，再执行
    递归删除。这样既满足“每次只保留最新精选结果”的需求，也避免误删工作区外文件。
    """

    root = output_root_dir.resolve()
    target = latest_stable_dir.resolve()
    if root != target and root not in target.parents:
        raise ValueError(f"拒绝清理 output_root_dir 之外的目录：{target}")
    if latest_stable_dir.exists():
        shutil.rmtree(latest_stable_dir)
    for name in ["figures", "reports"]:
        for category in ["core", "forward", "localization", "uncertainty", "diagnostics"]:
            (latest_stable_dir / name / category).mkdir(parents=True, exist_ok=True)
    for name in ["metadata"]:
        (latest_stable_dir / name).mkdir(parents=True, exist_ok=True)


def _copy_if_exists(src: Path, dst: Path, copied: list[str], missing: list[str]) -> None:
    """复制存在的精选文件；不存在时记录 missing，主流程不崩溃。"""

    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(str(dst))
    else:
        missing.append(str(src))


def _to_builtin(value: Any) -> Any:
    """把 numpy 标量/数组递归转成普通 Python 类型，避免 summary 出现 np.float64 表示。"""

    if value is None:
        return None
    if isinstance(value, dict):
        return {key: _to_builtin(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_builtin(item) for item in value]
    if hasattr(value, "tolist"):
        return value.tolist()
    if hasattr(value, "item"):
        try:
            return value.item()
        except ValueError:
            return value
    return value


def _format_optional(value: Any) -> str:
    return "无" if value is None else str(_to_builtin(value))


def _write_summary(summary_path: Path, summary_info: dict[str, Any], copied: list[str], missing: list[str]) -> None:
    """生成 latest_stable/summary.md 中文摘要。"""

    best = summary_info.get("best_location") or {}
    raw_best = summary_info.get("unweighted_best_location") or summary_info.get("raw_best_location") or {}
    weighted_best = summary_info.get("weighted_best_location") or {}
    raw_weighted_difference = summary_info.get("raw_weighted_difference") or {}
    truth_error = summary_info.get("truth_error") or {}
    confidence = summary_info.get("confidence") or {}
    recommendation = confidence.get("recommendation", {})
    high_region = confidence.get("high_score_region", {})
    score_method_comparison = summary_info.get("score_method_comparison") or {}
    depth_prior_sensitivity = summary_info.get("depth_prior_sensitivity") or {}
    stage4b_validation = summary_info.get("stage4b_validation") or {}
    stage5a_validation = summary_info.get("stage5a_validation") or {}
    stage5b_validation = summary_info.get("stage5b_validation") or {}
    preprocessing_ablation = stage4b_validation.get("preprocessing_ablation") or {}
    fk_validation = stage4b_validation.get("fk_filter_validation") or {}
    multi_attribute_ablation = stage4b_validation.get("multi_attribute_ablation") or {}
    geometry_ablation = stage4b_validation.get("geometry_ablation") or {}
    velocity_model_ablation = stage5a_validation.get("velocity_model_ablation") or {}
    model_mismatch = stage5a_validation.get("model_mismatch") or {}
    forward_engine_ablation = stage5b_validation.get("forward_engine_ablation") or {}
    forward_layered_vs_baseline = forward_engine_ablation.get("layered_vs_baseline") or {}
    forward_engines = forward_engine_ablation.get("engines") or {}
    acoustic2d = forward_engines.get("acoustic2d_prototype") or {}
    elastic_rayleigh = stage5b_validation.get("elastic2d_rayleigh_validation") or {}
    elastic_void = stage5b_validation.get("elastic2d_void_scattering") or {}
    elastic_das = stage5b_validation.get("elastic2d_das_response") or {}
    elastic_vs_kinematic = stage5b_validation.get("elastic_vs_kinematic") or {}
    velocity_model_audit = summary_info.get("velocity_model_audit") or {}
    velocity_model_visualization = summary_info.get("velocity_model_visualization") or {}
    figure_self_check = summary_info.get("figure_self_check") or {}
    scientific_figure_self_check = summary_info.get("scientific_figure_self_check") or {}
    repository_health = summary_info.get("repository_health") or {}
    stage5e_validation = summary_info.get("stage5e_validation") or {}
    elastic2d_numerical_sensitivity = stage5e_validation.get("elastic2d_numerical_sensitivity") or {}
    velocity_physics_bridge = stage5e_validation.get("velocity_model_physics_bridge") or {}
    das_nonzero = stage5e_validation.get("elastic2d_das_nonzero_check") or {}
    elastic_void_sensitivity = stage5b_validation.get("elastic2d_void_parameter_sensitivity") or {}
    peak = confidence.get("peak", {})
    contrast = confidence.get("contrast", {})
    consistency = confidence.get("multi_shot_consistency", {})
    coupling = confidence.get("y_depth_coupling", {})
    stage3b = confidence.get("stage3b_warnings", {})
    recommended = "\n".join(
        f"- {Path(path).resolve().relative_to(summary_path.parent.resolve()).as_posix()}"
        for path in copied
        if Path(path).resolve().is_relative_to(summary_path.parent.resolve())
        and ("figures" in Path(path).parts or "reports" in Path(path).parts)
    )
    scientific_recommended = scientific_figure_self_check.get("recommended_figures") or [
        "figures/core/fig_stage5e_status_badge.png",
        "figures/core/fig_confidence_diagnostics.png",
        "figures/diagnostics/fig_velocity_model_active_badge.png",
        "figures/diagnostics/fig_velocity_model_physics_bridge.png",
        "figures/diagnostics/fig_rayleigh_equivalent_vs_elastic_velocity.png",
        "figures/forward/fig_elastic2d_numerical_sensitivity_summary.png",
        "figures/forward/fig_elastic2d_rayleigh_pick_case_comparison.png",
        "figures/forward/fig_elastic2d_das_response_nonzero_check.png",
        "figures/forward/fig_elastic_vs_kinematic_energy_partition.png",
        "figures/localization/fig_scan_x_y_slice.png",
    ]
    scientific_recommended_text = "\n".join(f"- `{item}`" for item in scientific_recommended[:12])
    content = f"""# latest_stable 稳定成果摘要

## 本轮信息

- commit id：`{summary_info.get("commit_id", "unknown")}`
- 任务名称：`{summary_info.get("task_name", "Stage 5E")}`
- 运行时间：`{summary_info.get("run_time", datetime.now().isoformat(timespec="seconds"))}`
- 来源目录：`{summary_info.get("source_run_dir", "")}`

## 当前近似条件

- `kinematic approximation`
- `DAS-like response approximation`
- active forward engine：`{_format_optional(summary_info.get("forward_engine_active") or forward_engine_ablation.get("active_forward_engine"))}`
- available forward engines：`{_format_optional(summary_info.get("forward_engine_available") or forward_engine_ablation.get("available_forward_engines"))}`
- forward modeling stage：`{_format_optional(summary_info.get("forward_modeling_stage") or "F1 layered_kinematic + F2 acoustic2d validation")}`
- `kinematic_surface_response`，不是真实弹性波场模拟
- Rayleigh 深度权重是 `exp(-h / penetration_depth)` 简化近似，不是严格模态深度核

## 最佳定位结果

- best_location：x=`{_format_optional(best.get("x_m"))}` m，y=`{_format_optional(best.get("y_m"))}` m，h=`{_format_optional(best.get("depth_m"))}` m
- truth_error：`{_format_optional(truth_error.get("distance_m"))}` m

## unweighted 与 weighted best 对比

- unweighted_best：x=`{_format_optional(raw_best.get("x_m"))}` m，y=`{_format_optional(raw_best.get("y_m"))}` m，h=`{_format_optional(raw_best.get("depth_m"))}` m
- weighted_best：x=`{_format_optional(weighted_best.get("x_m"))}` m，y=`{_format_optional(weighted_best.get("y_m"))}` m，h=`{_format_optional(weighted_best.get("depth_m"))}` m
- unweighted -> weighted 差异：dx=`{_format_optional(raw_weighted_difference.get("dx_m"))}` m，dy=`{_format_optional(raw_weighted_difference.get("dy_m"))}` m，dh=`{_format_optional(raw_weighted_difference.get("ddepth_m"))}` m，三维距离=`{_format_optional(raw_weighted_difference.get("distance_m"))}` m

## 推荐位置与不确定性

- recommended_location_type：`{_format_optional(recommendation.get("recommended_location_type"))}`
- recommended_location：`{_format_optional(recommendation.get("recommended_location"))}`
- recommended_reason：{_format_optional(recommendation.get("recommended_location_reason"))}
- depth uncertainty interval：`{_format_optional(recommendation.get("depth_uncertainty_interval_m"))}` m
- 3D high-score span：x=`{_format_optional(high_region.get("x_span_m"))}` m，y=`{_format_optional(high_region.get("y_span_m"))}` m，depth=`{_format_optional(high_region.get("depth_span_m"))}` m
- high-score point count：`{_format_optional(high_region.get("high_score_region_point_count"))}`

## score method 对比

- comparison methods：`{list((score_method_comparison.get("methods") or {}).keys())}`
- depth stability reference：`{_format_optional(score_method_comparison.get("depth_stability_reference"))}`

## depth prior sensitivity

- factors：`{list((depth_prior_sensitivity.get("factors") or {}).keys())}`

## Stage 4B 算法有效性验证

- preprocessing best truth-error case：`{_format_optional(preprocessing_ablation.get("best_truth_error_case"))}`
- preprocessing narrowest y-depth case：`{_format_optional(preprocessing_ablation.get("narrowest_y_depth_case"))}`
- FK direct wave reduction ratio：`{_format_optional(fk_validation.get("direct_wave_reduction_ratio"))}`
- FK diffraction preservation ratio：`{_format_optional(fk_validation.get("diffraction_preservation_ratio"))}`
- multi_attribute improved over energy：`{_format_optional(multi_attribute_ablation.get("multi_attribute_improved_over_energy"))}`
- multi_attribute best group：`{_format_optional(multi_attribute_ablation.get("best_group_by_truth_error"))}`
- geometry best y-resolution case：`{_format_optional(geometry_ablation.get("best_y_resolution_case"))}`
- geometry best depth-stability case：`{_format_optional(geometry_ablation.get("best_depth_stability_case"))}`
- geometry best truth-error case：`{_format_optional(geometry_ablation.get("best_truth_error_case"))}`
- high-score component count：`{_format_optional(high_region.get("high_score_component_count"))}`
- multi-region warning：`{_format_optional(high_region.get("multi_region_warning"))}`

## Stage 5A 稳定算法与速度模型升级

- stable code area：`code/current_3d_algorithm/`
- default velocity model：`layered`
- velocity ablation best truth-error case：`{_format_optional(velocity_model_ablation.get("best_truth_error_case"))}`
- velocity ablation best depth case：`{_format_optional(velocity_model_ablation.get("best_depth_case"))}`
- largest travel-time residual case：`{_format_optional(velocity_model_ablation.get("largest_travel_time_residual_case"))}`
- model mismatch safest case：`{_format_optional(model_mismatch.get("safest_case"))}`
- model mismatch riskiest case：`{_format_optional(model_mismatch.get("riskiest_case"))}`
- minimum recommended velocity model：`{_format_optional(model_mismatch.get("minimum_recommended_velocity_model"))}`
- note：分层/非均匀速度仍是 straight-ray kinematic approximation，不是 3D elastic wavefield。

## Stage 5B/5C/5D 正演技术路线与 elastic2d 验证

- latest_stable_curated：`{_format_optional(summary_info.get("latest_stable_curated", True))}`
- forward_engine_active：`{_format_optional(summary_info.get("forward_engine_active") or forward_engine_ablation.get("active_forward_engine"))}`
- forward_engine_available：`{_format_optional(summary_info.get("forward_engine_available") or forward_engine_ablation.get("available_forward_engines"))}`
- forward_engine_next_required：`{_format_optional(summary_info.get("forward_engine_next_required") or forward_engine_ablation.get("next_required_forward"))}`
- forward_modeling_stage：`{_format_optional(summary_info.get("forward_modeling_stage") or "F1 layered_kinematic active, F2 acoustic2d validation, F3 elastic2d_prototype validation")}`
- validation_forward_available：`{_format_optional(summary_info.get("validation_forward_available") or ["acoustic2d_prototype", "elastic2d_prototype"])}`
- layered_vs_baseline travel-time RMS residual：`{_format_optional(forward_layered_vs_baseline.get("travel_time_residual_rms_ms"))}` ms
- layered_vs_baseline synthetic relative difference：`{_format_optional(forward_layered_vs_baseline.get("synthetic_relative_difference"))}`
- acoustic2d_prototype_status：CFL stable=`{_format_optional(acoustic2d.get("cfl_stable"))}`，snapshot_count=`{_format_optional(acoustic2d.get("snapshot_count"))}`
- elastic2d_prototype_status：`{_format_optional(summary_info.get("elastic2d_prototype_status") or "minimal_velocity_stress_validation")}`
- rayleigh_validation_status：`{_format_optional(summary_info.get("rayleigh_validation_status") or elastic_rayleigh.get("rayleigh_like_event_detected"))}`
- void_scattering_validation_status：`{_format_optional(summary_info.get("void_scattering_validation_status") or elastic_void.get("void_residual_visible"))}`
- das_gauge_response_status：`{_format_optional(summary_info.get("das_gauge_response_status") or elastic_das.get("status"))}`
- elastic_vs_kinematic_main_conclusion：{_format_optional(summary_info.get("elastic_vs_kinematic_main_conclusion") or elastic_vs_kinematic.get("main_conclusion"))}
- elastic2d_design_status：`{_format_optional(summary_info.get("elastic2d_design_status") or "minimal_prototype_available_validation_only")}`
- note：`acoustic2d_prototype` 是 acoustic wave-equation infrastructure validation，不能代表 Rayleigh/free-surface/void scattering；`elastic2d_prototype` 是最小科研验证原型，仍不替代主定位 forward。

## Stage 5D 速度模型核验、图件自检与 elastic2d 加固

- repository_health_status：`{_format_optional(repository_health.get("status"))}`
- figure_self_check_status：`{_format_optional(figure_self_check.get("status"))}`
- figure_self_check passed/failed：`{_format_optional(figure_self_check.get("passed_count"))}` / `{_format_optional(figure_self_check.get("failed_count"))}`
- active_velocity_model_type：`{_format_optional(velocity_model_audit.get("active_velocity_model_type") or summary_info.get("active_velocity_model_type"))}`
- active_velocity_model_confirmed：`{_format_optional(velocity_model_audit.get("active_velocity_model_confirmed"))}`
- velocity_model_used_by_direct：`{_format_optional(velocity_model_audit.get("velocity_model_used_by_direct"))}`
- velocity_model_used_by_scatter：`{_format_optional(velocity_model_audit.get("velocity_model_used_by_scatter"))}`
- velocity_model_used_by_scan：`{_format_optional(velocity_model_audit.get("velocity_model_used_by_scan"))}`
- velocity_model_visualization_status：`{_format_optional(velocity_model_visualization.get("status"))}`
- uniform_vs_layered_direct_rms_ms：`{_format_optional((velocity_model_visualization.get("uniform_vs_active_travel_time_difference") or {}).get("direct_diff_rms_ms"))}`
- rayleigh_like_event_detected：`{_format_optional(elastic_rayleigh.get("rayleigh_like_event_detected"))}`
- rayleigh_pick_interpretation：{_format_optional(elastic_rayleigh.get("rayleigh_pick_interpretation"))}
- void_residual_energy_best_case：`{_format_optional(elastic_void_sensitivity.get("best_case"))}` / `{_format_optional(elastic_void_sensitivity.get("best_residual_energy"))}`
- das_gauge_response_best_case：source=`{_format_optional(elastic_das.get("best_source_type_for_gauge"))}`，gauge_length=`{_format_optional(elastic_das.get("best_gauge_length_m"))}` m
- elastic_vs_kinematic_explained_fraction：`{_format_optional(elastic_vs_kinematic.get("kinematic_curve_explained_fraction"))}`

## Stage 5E 科学图件自检、速度物理桥接与 elastic2d 数值加固

- stage：`Stage 5E`
- scientific_figure_self_check_status：`{_format_optional(scientific_figure_self_check.get("status"))}`
- scientific warning count：`{_format_optional(scientific_figure_self_check.get("scientific_warning_count"))}`
- rayleigh_like_event_best_case：`{_format_optional(elastic2d_numerical_sensitivity.get("best_case"))}`
- rayleigh_like_event_detected：`{_format_optional(elastic2d_numerical_sensitivity.get("rayleigh_like_event_detected_any") if elastic2d_numerical_sensitivity else elastic_rayleigh.get("rayleigh_like_event_detected"))}`
- elastic2d_best_numerical_case：`{_format_optional(elastic2d_numerical_sensitivity.get("best_case_metrics"))}`
- velocity_physics_bridge_status：`{_format_optional(velocity_physics_bridge.get("status"))}`
- rayleigh_equivalent_vs_elastic_consistency：`{_format_optional(velocity_physics_bridge.get("rayleigh_equivalent_vs_elastic_consistency"))}`
- das_gauge_nonzero_status：`{_format_optional(das_nonzero.get("das_gauge_nonzero_status"))}`
- das gauge default localization enabled：`{_format_optional(das_nonzero.get("default_localization_should_use_gauge_strain"))}`
- elastic2d_ready_for_2p5d：`{_format_optional(elastic2d_numerical_sensitivity.get("elastic2d_ready_for_2p5d"))}`

## Stage 5E 人工优先查看图件

{scientific_recommended_text}

## 基础置信度指标

- peak sharpness：`{_format_optional(peak.get("peak_sharpness"))}`
- score contrast：`{_format_optional(contrast.get("score_contrast"))}`
- score percentile：`{_format_optional(contrast.get("score_percentile"))}`
- multi-shot consistency CV：`{_format_optional(consistency.get("coefficient_of_variation"))}`
- y-depth coupling warning：`{_format_optional(coupling.get("warning"))}`
- best depth boundary warning：`{_format_optional(stage3b.get("best_depth_at_boundary_warning"))}`
- wide y high-score zone warning：`{_format_optional(stage3b.get("wide_y_high_score_zone_warning"))}`
- raw/weighted divergence warning：`{_format_optional(stage3b.get("raw_weighted_divergence_warning"))}`
- shallow bias warning：`{_format_optional(stage3b.get("shallow_bias_warning"))}`
- low confidence flag：`{confidence.get("low_confidence_flag", "unknown")}`

## 推荐人工重点查看

{recommended}

## 导出记录

- 已复制精选文件数量：`{len(copied)}`
- 缺失精选文件数量：`{len(missing)}`

## 当前限制

本目录只保存本轮最新、最值得人工检查的精选结果。时间戳运行目录保留完整本地结果，但大型数组、快照和中间产物默认不纳入 Git。当前定位和置信度仍是科研算法原型诊断，不能作为工程确诊结论。
"""
    summary_path.write_text(content, encoding="utf-8")


def _write_latest_stable_readme(path: Path) -> None:
    """写出 latest_stable 精选目录说明。"""

    lines = [
        "# latest_stable curated outputs",
        "",
        "本目录只保存当前阶段最关键的稳定精选成果，不再作为历史阶段文件堆积目录。",
        "",
        "## 子目录",
        "",
        "- `figures/core/`：人工复查最优先图件。",
        "- `figures/forward/`：forward roadmap、acoustic2d、elastic2d 验证图件。",
        "- `figures/localization/`：定位与多属性评分图件。",
        "- `figures/uncertainty/`：三维不确定性和推荐决策图件。",
        "- `figures/diagnostics/`：速度模型、模型错配和 depth prior 诊断。",
        "- `reports/core/`：核心报告。",
        "- `reports/forward/`：正演验证报告。",
        "- `reports/localization/`：定位验证报告。",
        "- `reports/diagnostics/`：速度模型和模型错配报告。",
        "",
        "当前结果仍是科研候选区，不是工程确诊。",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_archive_manifest(path: Path) -> None:
    """记录不再进入 curated latest_stable 的历史输出类型。"""

    lines = [
        "# archive manifest",
        "",
        "Stage 5C 起，latest_stable 不再平铺保存所有历史阶段图件和报告。",
        "",
        "## 不再作为当前主结论平铺保存的内容",
        "",
    ]
    lines.extend(f"- {item}" for item in LEGACY_STABLE_FILES)
    lines.extend(
        [
            "",
            "完整历史输出仍保存在对应时间戳运行目录；Git 中的 latest_stable 只保留当前精选成果。",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def export_latest_stable_outputs(
    run_output_dir: Path,
    latest_stable_dir: Path,
    summary_info: dict[str, Any],
) -> dict[str, Any]:
    """导出最新稳定精选成果。

    输入：
        run_output_dir：本次时间戳运行目录；
        latest_stable_dir：固定精选目录，通常为 outputs/latest_stable；
        summary_info：best_location、truth_error、confidence 等摘要信息。

    行为：
        1. 清理旧 latest_stable；
        2. 只复制精选图件、动图、报告和 metadata；
        3. 生成 summary.md；
        4. 返回 copied/missing 列表，供 metadata 和测试使用。
    """

    run_output_dir = Path(run_output_dir)
    latest_stable_dir = Path(latest_stable_dir)
    output_root_dir = latest_stable_dir.parent
    figure_metadata = build_figure_metadata(
        stage="Stage 5E",
        forward_engine=str(summary_info.get("forward_engine_active", "layered_kinematic")),
        velocity_model_type=str(summary_info.get("active_velocity_model_type", "layered")),
    )
    figure_self_check = run_figure_self_check(run_output_dir, STAGE5E_FIGURE_SPECS, figure_metadata)
    write_figure_self_check_report(
        run_output_dir / "reports" / "report_figure_self_check.md",
        figure_self_check,
    )
    passed_by_category: dict[str, set[str]] = {}
    for item in figure_self_check["passed_items"]:
        passed_by_category.setdefault(item["category"], set()).add(item["filename"])
    _reset_latest_stable_dir(latest_stable_dir, output_root_dir)

    copied: list[str] = []
    missing: list[str] = []
    for category, filenames in CURATED_FIGURES.items():
        for filename in filenames:
            if filename not in passed_by_category.get(category, set()):
                missing.append(str(run_output_dir / "figures" / filename))
                continue
            _copy_if_exists(
                run_output_dir / "figures" / filename,
                latest_stable_dir / "figures" / category / filename,
                copied,
                missing,
            )
    _copy_if_exists(
        run_output_dir / "animations" / "anim_pseudo_wavefield.gif",
        latest_stable_dir / "figures" / "diagnostics" / "anim_pseudo_wavefield.gif",
        copied,
        missing,
    )
    for category, filenames in CURATED_REPORTS.items():
        for filename in filenames:
            _copy_if_exists(
                run_output_dir / "reports" / filename,
                latest_stable_dir / "reports" / category / filename,
                copied,
                missing,
            )
    _copy_if_exists(
        run_output_dir / "metadata" / "meta_run.json",
        latest_stable_dir / "metadata" / "meta_run.json",
        copied,
        missing,
    )
    _copy_if_exists(
        run_output_dir / "metadata" / "params_snapshot.json",
        latest_stable_dir / "metadata" / "meta_params_snapshot.json",
        copied,
        missing,
    )
    manifest_path = latest_stable_dir / "metadata" / "figure_manifest.json"
    manifest_path.write_text(json.dumps(figure_self_check, ensure_ascii=False, indent=2), encoding="utf-8")
    copied.append(str(manifest_path))
    summary_info["figure_self_check"] = {
        "checked_count": figure_self_check["checked_count"],
        "passed_count": figure_self_check["passed_count"],
        "failed_count": figure_self_check["failed_count"],
        "status": figure_self_check["status"],
        "excluded_old_figures": figure_self_check["excluded_old_figures"],
        "excluded_duplicate_figures": figure_self_check["excluded_duplicate_figures"],
    }
    _write_latest_stable_readme(latest_stable_dir / "README.md")
    copied.append(str(latest_stable_dir / "README.md"))
    _write_archive_manifest(latest_stable_dir / "archive_manifest.md")
    copied.append(str(latest_stable_dir / "archive_manifest.md"))
    _write_summary(latest_stable_dir / "summary.md", summary_info, copied, missing)
    copied.append(str(latest_stable_dir / "summary.md"))
    repository_health = build_repository_health_report(Path.cwd(), latest_stable_dir)
    repository_health_path = latest_stable_dir / "reports" / "core" / "report_repository_health.md"
    write_repository_health_report(repository_health_path, repository_health)
    # repository health 报告自身写入后，reports/core 数量会增加 1。
    # 重新统计一次，保证报告中的 latest_stable 分层数量与最终目录完全一致。
    repository_health = build_repository_health_report(Path.cwd(), latest_stable_dir)
    write_repository_health_report(repository_health_path, repository_health)
    copied.append(str(repository_health_path))
    summary_info["repository_health"] = {
        "status": repository_health["status"],
        "figures_root_png_count": repository_health["figures_root_png_count"],
        "reports_root_md_count": repository_health["reports_root_md_count"],
    }
    scientific_check = run_scientific_figure_self_check(latest_stable_dir, summary_info)
    scientific_path = latest_stable_dir / "reports" / "core" / "report_scientific_figure_self_check.md"
    write_scientific_figure_self_check_report(scientific_path, scientific_check)
    copied.append(str(scientific_path))
    summary_info["scientific_figure_self_check"] = {
        "status": scientific_check["status"],
        "checked_figure_count": scientific_check["checked_figure_count"],
        "scientific_warning_count": scientific_check["scientific_warning_count"],
        "failure_count": scientific_check["failure_count"],
        "recommended_figures": scientific_check["recommended_figures"],
    }
    repository_health = build_repository_health_report(Path.cwd(), latest_stable_dir)
    write_repository_health_report(repository_health_path, repository_health)
    summary_info["repository_health"] = {
        "status": repository_health["status"],
        "figures_root_png_count": repository_health["figures_root_png_count"],
        "reports_root_md_count": repository_health["reports_root_md_count"],
    }
    _write_summary(latest_stable_dir / "summary.md", summary_info, copied, missing)
    return {
        "latest_stable_dir": str(latest_stable_dir),
        "copied": copied,
        "missing": missing,
        "summary_path": str(latest_stable_dir / "summary.md"),
    }
