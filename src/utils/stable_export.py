"""导出 outputs/latest_stable 精选稳定成果。"""

from __future__ import annotations

import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


SELECTED_FIGURES = [
    "fig_geometry_layout_check.png",
    "fig_source_anomaly_receiver_path_section.png",
    "fig_rayleigh_depth_sensitivity.png",
    "fig_shot_gather_000.png",
    "fig_diffraction_travel_time_curves.png",
    "fig_scan_x_depth_slice.png",
    "fig_scan_x_y_slice.png",
    "fig_best_location_map.png",
    "fig_raw_vs_weighted_best_location.png",
    "fig_raw_vs_weighted_x_depth_slice.png",
    "fig_y_high_score_width_check.png",
    "fig_confidence_diagnostics.png",
    "fig_score_method_depth_comparison.png",
    "fig_3d_high_score_uncertainty_summary.png",
    "fig_x_y_depth_uncertainty_slices.png",
    "fig_3d_geometry_overview.png",
    "fig_receiver_source_3d_layout.png",
    "fig_anomaly_3d_scatter_points.png",
    "fig_multi_attribute_score_comparison.png",
    "fig_depth_prior_sensitivity.png",
    "fig_preprocessing_comparison.png",
    "fig_preprocessing_ablation_summary.png",
    "fig_fk_spectrum_before_after.png",
    "fig_fk_filter_effect_on_gather.png",
    "fig_matched_wavelet_score_comparison.png",
    "fig_semblance_score_volume_slice.png",
    "fig_frequency_shift_attribute.png",
    "fig_geometry_ablation_best_locations.png",
    "fig_geometry_ablation_uncertainty_spans.png",
    "fig_multi_attribute_ablation.png",
    "fig_3d_high_score_components.png",
    "fig_recommendation_decision_flow.png",
    "fig_velocity_model_comparison.png",
    "fig_layered_velocity_profile.png",
    "fig_velocity_model_travel_time_residuals.png",
    "fig_model_mismatch_error_summary.png",
]

SELECTED_REPORTS = [
    "report_full_pipeline.md",
    "report_confidence.md",
    "report_score_method_comparison.md",
    "report_depth_prior_sensitivity.md",
    "report_preprocessing_ablation.md",
    "report_fk_filter_validation.md",
    "report_matched_wavelet_validation.md",
    "report_semblance_validation.md",
    "report_frequency_shift_attribute.md",
    "report_geometry_ablation.md",
    "report_multi_attribute_ablation.md",
    "report_velocity_model_ablation.md",
    "report_model_mismatch.md",
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
    for name in ["figures", "animations", "reports", "metadata"]:
        (latest_stable_dir / name).mkdir(parents=True, exist_ok=True)


def _copy_if_exists(src: Path, dst: Path, copied: list[str], missing: list[str]) -> None:
    """复制存在的精选文件；不存在时记录 missing，主流程不崩溃。"""

    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(str(dst))
    else:
        missing.append(str(src))


def _format_optional(value: Any) -> str:
    return "无" if value is None else str(value)


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
    preprocessing_ablation = stage4b_validation.get("preprocessing_ablation") or {}
    fk_validation = stage4b_validation.get("fk_filter_validation") or {}
    multi_attribute_ablation = stage4b_validation.get("multi_attribute_ablation") or {}
    geometry_ablation = stage4b_validation.get("geometry_ablation") or {}
    velocity_model_ablation = stage5a_validation.get("velocity_model_ablation") or {}
    model_mismatch = stage5a_validation.get("model_mismatch") or {}
    peak = confidence.get("peak", {})
    contrast = confidence.get("contrast", {})
    consistency = confidence.get("multi_shot_consistency", {})
    coupling = confidence.get("y_depth_coupling", {})
    stage3b = confidence.get("stage3b_warnings", {})
    recommended = "\n".join(
        [
            "- figures/fig_geometry_layout_check.png",
            "- figures/fig_source_anomaly_receiver_path_section.png",
            "- figures/fig_rayleigh_depth_sensitivity.png",
            "- figures/fig_shot_gather_000.png",
            "- figures/fig_diffraction_travel_time_curves.png",
            "- figures/fig_scan_x_depth_slice.png",
            "- figures/fig_scan_x_y_slice.png",
            "- figures/fig_best_location_map.png",
            "- figures/fig_raw_vs_weighted_best_location.png",
            "- figures/fig_raw_vs_weighted_x_depth_slice.png",
            "- figures/fig_y_high_score_width_check.png",
            "- figures/fig_confidence_diagnostics.png",
            "- figures/fig_score_method_depth_comparison.png",
            "- figures/fig_3d_high_score_uncertainty_summary.png",
            "- figures/fig_x_y_depth_uncertainty_slices.png",
            "- figures/fig_3d_geometry_overview.png",
            "- figures/fig_receiver_source_3d_layout.png",
            "- figures/fig_anomaly_3d_scatter_points.png",
            "- figures/fig_multi_attribute_score_comparison.png",
            "- figures/fig_depth_prior_sensitivity.png",
            "- figures/fig_preprocessing_comparison.png",
            "- figures/fig_preprocessing_ablation_summary.png",
            "- figures/fig_fk_spectrum_before_after.png",
            "- figures/fig_fk_filter_effect_on_gather.png",
            "- figures/fig_matched_wavelet_score_comparison.png",
            "- figures/fig_semblance_score_volume_slice.png",
            "- figures/fig_frequency_shift_attribute.png",
            "- figures/fig_geometry_ablation_best_locations.png",
            "- figures/fig_geometry_ablation_uncertainty_spans.png",
            "- figures/fig_multi_attribute_ablation.png",
            "- figures/fig_3d_high_score_components.png",
            "- figures/fig_recommendation_decision_flow.png",
            "- figures/fig_velocity_model_comparison.png",
            "- figures/fig_layered_velocity_profile.png",
            "- figures/fig_velocity_model_travel_time_residuals.png",
            "- figures/fig_model_mismatch_error_summary.png",
            "- animations/anim_pseudo_wavefield.gif",
            "- reports/report_full_pipeline.md",
            "- reports/report_confidence.md",
            "- reports/report_score_method_comparison.md",
            "- reports/report_depth_prior_sensitivity.md",
            "- reports/report_preprocessing_ablation.md",
            "- reports/report_fk_filter_validation.md",
            "- reports/report_matched_wavelet_validation.md",
            "- reports/report_semblance_validation.md",
            "- reports/report_frequency_shift_attribute.md",
            "- reports/report_geometry_ablation.md",
            "- reports/report_multi_attribute_ablation.md",
            "- reports/report_velocity_model_ablation.md",
            "- reports/report_model_mismatch.md",
        ]
    )
    content = f"""# latest_stable 稳定成果摘要

## 本轮信息

- commit id：`{summary_info.get("commit_id", "unknown")}`
- 任务名称：`{summary_info.get("task_name", "Stage 5A")}`
- 运行时间：`{summary_info.get("run_time", datetime.now().isoformat(timespec="seconds"))}`
- 来源目录：`{summary_info.get("source_run_dir", "")}`

## 当前近似条件

- `kinematic approximation`
- `DAS-like response approximation`
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
    _reset_latest_stable_dir(latest_stable_dir, output_root_dir)

    copied: list[str] = []
    missing: list[str] = []
    for filename in SELECTED_FIGURES:
        _copy_if_exists(
            run_output_dir / "figures" / filename,
            latest_stable_dir / "figures" / filename,
            copied,
            missing,
        )
    _copy_if_exists(
        run_output_dir / "animations" / "anim_pseudo_wavefield.gif",
        latest_stable_dir / "animations" / "anim_pseudo_wavefield.gif",
        copied,
        missing,
    )
    for filename in SELECTED_REPORTS:
        _copy_if_exists(
            run_output_dir / "reports" / filename,
            latest_stable_dir / "reports" / filename,
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
    _write_summary(latest_stable_dir / "summary.md", summary_info, copied, missing)
    copied.append(str(latest_stable_dir / "summary.md"))
    return {
        "latest_stable_dir": str(latest_stable_dir),
        "copied": copied,
        "missing": missing,
        "summary_path": str(latest_stable_dir / "summary.md"),
    }
