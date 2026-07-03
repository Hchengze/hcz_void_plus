"""Stage 4A full_pipeline：参考审计接入 + 三维几何 + 预处理 + 多属性扫描 + 稳定成果导出。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np

from src.confidence.confidence_report import build_confidence_metrics, write_confidence_report
from src.localization.scan_grid import build_scan_grid
from src.localization.travel_time import compute_candidate_diffraction_times
from src.localization.depth_prior_sensitivity import run_depth_prior_sensitivity
from src.localization.score_method_comparison import run_score_method_comparison
from src.pipeline.run_forward_pipeline import run_forward_pipeline
from src.pipeline.run_scan_pipeline import run_scan_pipeline
from src.utils.metadata import build_metadata, save_json
from src.utils.stable_export import export_latest_stable_outputs, get_git_commit_id
from src.visualization.plot_confidence import plot_confidence_diagnostics
from src.visualization.plot_scan import plot_y_high_score_width_check
from src.visualization.plot_uncertainty import (
    plot_3d_high_score_uncertainty_summary,
    plot_depth_prior_sensitivity,
    plot_multi_attribute_score_comparison,
    plot_score_method_depth_comparison,
    plot_x_y_depth_uncertainty_slices,
)
from src.validation.common import summarize_volume
from src.validation.fk_filter_validation import run_fk_filter_validation
from src.validation.geometry_ablation import run_geometry_ablation
from src.validation.model_mismatch import run_model_mismatch_experiment
from src.validation.multi_attribute_ablation import run_multi_attribute_ablation
from src.validation.preprocessing_ablation import run_preprocessing_ablation
from src.validation.reports import (
    write_attribute_validation_report,
    write_fk_filter_validation_report,
    write_geometry_ablation_report,
    write_model_mismatch_report,
    write_multi_attribute_ablation_report,
    write_preprocessing_ablation_report,
    write_velocity_model_ablation_report,
)
from src.validation.velocity_model_ablation import run_velocity_model_ablation
from src.visualization.plot_stage4b import (
    plot_3d_high_score_components,
    plot_fk_filter_effect_on_gather,
    plot_fk_spectrum_before_after,
    plot_frequency_shift_attribute,
    plot_geometry_ablation_best_locations,
    plot_geometry_ablation_uncertainty_spans,
    plot_matched_wavelet_score_comparison,
    plot_multi_attribute_ablation,
    plot_preprocessing_ablation_summary,
    plot_recommendation_decision_flow,
    plot_semblance_score_volume_slice,
)
from src.visualization.plot_stage5a import (
    plot_layered_velocity_profile,
    plot_model_mismatch_error_summary,
    plot_velocity_model_comparison,
    plot_velocity_model_travel_time_residuals,
)


def _write_full_pipeline_report(
    params: SimpleNamespace,
    output_path: Path,
    scan_result: dict[str, Any],
    confidence_metrics: dict[str, Any] | None = None,
) -> None:
    """写出综合中文报告。"""

    best = scan_result["best_location"]
    error = scan_result["truth_error"]
    unweighted_best = scan_result["unweighted_best_location"]
    weighted_best = scan_result["weighted_best_location"]
    diff = scan_result["raw_weighted_difference"]
    recommended_text = "本次未生成推荐位置。"
    confidence_text = "本次未执行基础置信度分析。"
    if confidence_metrics is not None:
        peak = confidence_metrics["peak"]
        contrast = confidence_metrics["contrast"]
        consistency = confidence_metrics["multi_shot_consistency"]
        coupling = confidence_metrics["y_depth_coupling"]
        stage3b = confidence_metrics["stage3b_warnings"]
        recommendation = confidence_metrics["recommendation"]
        high_region = confidence_metrics["high_score_region"]
        recommended_text = f"""- recommended_location_type：`{recommendation["recommended_location_type"]}`
- recommended_location：`{recommendation["recommended_location"]}`
- recommended_reason：{recommendation["recommended_location_reason"]}
- depth uncertainty interval：`{recommendation["depth_uncertainty_interval_m"]}` m
- 3D high-score span：x=`{high_region["x_span_m"]}` m，y=`{high_region["y_span_m"]}` m，depth=`{high_region["depth_span_m"]}` m"""
        confidence_text = f"""- peak sharpness：`{peak["peak_sharpness"]:.4g}`
- score contrast：`{contrast["score_contrast"]:.4g}`
- score percentile：`{contrast["score_percentile"]:.2f}%`
- multi-shot consistency CV：`{consistency["coefficient_of_variation"]:.4g}`
- y-depth coupling warning：`{coupling["warning"]}`
- best_depth_at_boundary_warning：`{stage3b["best_depth_at_boundary_warning"]}`
- wide_y_high_score_zone_warning：`{stage3b["wide_y_high_score_zone_warning"]}`
- raw_weighted_divergence_warning：`{stage3b["raw_weighted_divergence_warning"]}`
- shallow_bias_warning：`{stage3b["shallow_bias_warning"]}`
- confidence flag：`{confidence_metrics["low_confidence_flag"]}`

这些指标只是规则型科研诊断，用于帮助人工判断结果是否稳定，不能作为工程确诊。"""
    content = f"""# Full Pipeline 综合报告

本次运行完成：DAS-like 运动学多炮正演、三维观测几何诊断、基础预处理、多属性 x-y-h 扫描定位、深度先验敏感性诊断和规则型稳定性自检。

## 当前近似条件

- forward：`kinematic approximation`
- DAS-like：`DAS-like response approximation`
- velocity：`{params.velocity.model_type}`，支持 uniform / layered / lateral gradient / localized low velocity zone
- velocity approximation：`straight-ray kinematic approximation`，不是弹性波速度反演
- surface response：`kinematic_surface_response_snapshot`，只是 Rayleigh 波走时控制的地表响应示意，不是真实弹性波模拟
- Rayleigh depth sensitivity：`exp(-h / penetration_depth)` 简化权重，不是严格模态深度核

## 扫描结果

- score method：`{params.scan.score_method}`
- score volume shape：`{tuple(scan_result["score_volume"].shape)}`
- arr_score_volume.npy 当前主结果：`{scan_result["score_volume_kind"]}`
- active score kind：`{scan_result["score_volume_active_kind"]}`
- scan score mode：`{params.scan.score_mode}`
- scan depth weighting：`{params.scan.use_depth_weight}`
- best_location：x=`{best["x_m"]}` m，y=`{best["y_m"]}` m，h=`{best["depth_m"]}` m
- truth_error distance：`{error["distance_m"]}` m

## raw 与 weighted best 对比

- unweighted_best：x=`{unweighted_best["x_m"]}` m，y=`{unweighted_best["y_m"]}` m，h=`{unweighted_best["depth_m"]}` m
- weighted_best：x=`{weighted_best["x_m"]}` m，y=`{weighted_best["y_m"]}` m，h=`{weighted_best["depth_m"]}` m
- unweighted -> weighted 差异：dx=`{diff["dx_m"]}` m，dy=`{diff["dy_m"]}` m，dh=`{diff["ddepth_m"]}` m，三维距离=`{diff["distance_m"]}` m
- depth_prior_bias_warning：`{scan_result["depth_prior_bias_warning"]}`

## 推荐位置与三维不确定性

{recommended_text}

## 基础置信度分析

{confidence_text}

## Stage 4B 有效性验证

本轮额外输出预处理消融、FK 滤波验证、matched wavelet、semblance、frequency shift、多属性消融、三维几何消融、三维高分区连通域和推荐决策流程图。若这些验证没有改善 y/depth 不确定性，报告必须解释为“接口已建立，效果待验证”，不能把候选点写成工程确诊。

## Stage 5A 速度模型升级

本轮新增 layered / lateral_gradient / localized_low_velocity_zone / layered_with_anomaly_perturbation 速度模型，并输出 velocity model ablation 与 model mismatch 报告。分层和非均匀速度会改变绕射走时曲线与扫描结果，但当前仍是 straight-ray kinematic approximation，不是 3D elastic wavefield。

## 风险提示

单侧 DAS-like 几何下 y-depth 可能耦合。best_location 是运动学局部能量聚焦结果，不能作为工程确诊结论。
"""
    output_path.write_text(content, encoding="utf-8")


def _write_score_method_comparison_report(
    params: SimpleNamespace,
    output_path: Path,
    comparison_result: dict[str, Any],
) -> None:
    """写出 score_method 轻量对比报告。"""

    lines = [
        "# score_method 轻量对比报告",
        "",
        "本报告只比较同一数据、同一扫描网格下的 score_method，不是大规模鲁棒性扫描。",
        "",
        "| score_method | unweighted_best | weighted_best | unweighted_error_m | weighted_error_m | weighted_depth_at_boundary |",
        "|---|---|---|---:|---:|---|",
    ]
    for method, result in comparison_result["methods"].items():
        unweighted = result["unweighted_best_location"]
        weighted = result["weighted_best_location"]
        lines.append(
            "| "
            f"{method} | "
            f"x={unweighted['x_m']}, y={unweighted['y_m']}, h={unweighted['depth_m']} | "
            f"x={weighted['x_m']}, y={weighted['y_m']}, h={weighted['depth_m']} | "
            f"{result['unweighted_truth_error']['distance_m']:.4g} | "
            f"{result['weighted_truth_error']['distance_m']:.4g} | "
            f"{result['weighted_depth_at_boundary']} |"
        )
    reference = comparison_result["depth_stability_reference"]
    lines.extend(
        [
            "",
            "## 深度稳定性参考",
            "",
            f"- best_unweighted_depth_method：`{reference['best_unweighted_depth_method']}`",
            f"- best_unweighted_depth_abs_error_m：`{reference['best_unweighted_depth_abs_error_m']}`",
            f"- 说明：{reference['note']}",
            "",
            "当前对比仍基于运动学 DAS-like 数据，不能作为工程确诊。",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _write_depth_prior_sensitivity_report(output_path: Path, sensitivity_result: dict[str, Any]) -> None:
    """写出 depth prior 敏感性中文报告。"""

    lines = [
        "# depth prior 敏感性报告",
        "",
        "本报告基于 unweighted score volume 快速评估不同 Rayleigh depth prior 因子对 best depth 的影响。",
        "",
        "| factor | penetration_depth_m | best_location | best_depth_at_boundary |",
        "|---|---:|---|---|",
    ]
    for factor, result in sensitivity_result["factors"].items():
        lines.append(
            f"| {factor} | {result['penetration_depth_m']} | {result['best_location']} | {result['best_depth_at_boundary']} |"
        )
    lines.append("\n该诊断不是严格 Rayleigh 模态核，只用于检查 depth prior 是否支配定位结果。")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _build_final_metadata(
    params: SimpleNamespace,
    forward_result: dict[str, Any],
    scan_result: dict[str, Any],
    confidence_metrics: dict[str, Any],
    score_method_comparison: dict[str, Any] | None,
    depth_prior_sensitivity: dict[str, Any] | None,
    stage4b_validation: dict[str, Any] | None,
    stage5a_validation: dict[str, Any] | None,
    latest_stable_path: Path | None,
    latest_stable_exported: bool,
) -> dict[str, Any]:
    """在 full_pipeline 收尾阶段写出包含置信度和稳定导出状态的 metadata。"""

    paths = forward_result["paths"]
    git_info = {
        "commit_id": get_git_commit_id(Path.cwd()),
        # pipeline 只能记录“本轮预期会 push”的工作流状态；真正 push 成功与否由收尾 git push 命令确认。
        "push_attempted": True,
        "push_success": False,
    }
    output_info = {
        "latest_stable_exported": latest_stable_exported,
        "latest_stable_path": str(latest_stable_path) if latest_stable_path is not None else None,
    }
    metadata = build_metadata(
        params,
        forward_result["synthetic_data"],
        forward_result["scatter_xyz"],
        forward_result["scatter_weight"],
        font_info=forward_result.get("font_info", {}),
        wavefield_info=forward_result.get("wavefield_info", {}),
        scan_result=scan_result,
        diagnostics_info={
            "diffraction_travel_time_curve_figure": str(paths["figures"] / "fig_diffraction_travel_time_curves.png"),
            "path_section_figure": str(paths["figures"] / "fig_source_anomaly_receiver_path_section.png"),
            "depth_sensitivity_figure": str(paths["figures"] / "fig_rayleigh_depth_sensitivity.png"),
            "raw_vs_weighted_best_location_figure": str(paths["figures"] / "fig_raw_vs_weighted_best_location.png"),
            "raw_vs_weighted_x_depth_slice_figure": str(paths["figures"] / "fig_raw_vs_weighted_x_depth_slice.png"),
            "y_high_score_width_check_figure": str(paths["figures"] / "fig_y_high_score_width_check.png"),
            "score_method_depth_comparison_figure": str(paths["figures"] / "fig_score_method_depth_comparison.png"),
            "3d_high_score_uncertainty_summary_figure": str(paths["figures"] / "fig_3d_high_score_uncertainty_summary.png"),
            "x_y_depth_uncertainty_slices_figure": str(paths["figures"] / "fig_x_y_depth_uncertainty_slices.png"),
            "multi_attribute_score_comparison_figure": str(paths["figures"] / "fig_multi_attribute_score_comparison.png"),
            "depth_prior_sensitivity_figure": str(paths["figures"] / "fig_depth_prior_sensitivity.png"),
            "preprocessing_comparison_figure": str(paths["figures"] / "fig_preprocessing_comparison.png"),
            "preprocessing_ablation_summary_figure": str(paths["figures"] / "fig_preprocessing_ablation_summary.png"),
            "fk_spectrum_before_after_figure": str(paths["figures"] / "fig_fk_spectrum_before_after.png"),
            "fk_filter_effect_on_gather_figure": str(paths["figures"] / "fig_fk_filter_effect_on_gather.png"),
            "matched_wavelet_score_comparison_figure": str(paths["figures"] / "fig_matched_wavelet_score_comparison.png"),
            "semblance_score_volume_slice_figure": str(paths["figures"] / "fig_semblance_score_volume_slice.png"),
            "frequency_shift_attribute_figure": str(paths["figures"] / "fig_frequency_shift_attribute.png"),
            "geometry_ablation_best_locations_figure": str(paths["figures"] / "fig_geometry_ablation_best_locations.png"),
            "geometry_ablation_uncertainty_spans_figure": str(paths["figures"] / "fig_geometry_ablation_uncertainty_spans.png"),
            "multi_attribute_ablation_figure": str(paths["figures"] / "fig_multi_attribute_ablation.png"),
            "3d_high_score_components_figure": str(paths["figures"] / "fig_3d_high_score_components.png"),
            "recommendation_decision_flow_figure": str(paths["figures"] / "fig_recommendation_decision_flow.png"),
            "velocity_model_comparison_figure": str(paths["figures"] / "fig_velocity_model_comparison.png"),
            "layered_velocity_profile_figure": str(paths["figures"] / "fig_layered_velocity_profile.png"),
            "velocity_model_travel_time_residuals_figure": str(
                paths["figures"] / "fig_velocity_model_travel_time_residuals.png"
            ),
            "model_mismatch_error_summary_figure": str(paths["figures"] / "fig_model_mismatch_error_summary.png"),
        },
        confidence_info=confidence_metrics,
        score_method_comparison=score_method_comparison,
        depth_prior_sensitivity=depth_prior_sensitivity,
        output_info=output_info,
        git_info=git_info,
    )
    metadata["stage4b_validation"] = stage4b_validation or {}
    metadata["stage5a_validation"] = stage5a_validation or {}
    save_json(paths["metadata"] / "meta_run.json", metadata)
    return metadata


def run_full_pipeline(params: SimpleNamespace) -> dict[str, Any]:
    """运行 Stage 4A 完整闭环。

    流程顺序：
        1. 运动学 DAS-like 正演；
        2. 三维观测几何与异常体散射点诊断；
        3. 基础预处理；
        4. 多属性 x-y-h 扫描定位；
        5. 规则型置信度、三维高分区和 depth prior 敏感性诊断；
        6. 综合报告、metadata 和 outputs/latest_stable 精选成果导出。
    """

    forward_result = run_forward_pipeline(params)
    scan_result: dict[str, Any] | None = None
    confidence_metrics: dict[str, Any] | None = None
    stable_export_info: dict[str, Any] | None = None
    score_method_comparison: dict[str, Any] | None = None
    depth_prior_sensitivity: dict[str, Any] | None = None
    preprocessing_ablation: dict[str, Any] | None = None
    fk_validation: dict[str, Any] | None = None
    multi_attribute_ablation: dict[str, Any] | None = None
    geometry_ablation: dict[str, Any] | None = None
    velocity_model_ablation: dict[str, Any] | None = None
    model_mismatch: dict[str, Any] | None = None
    if params.scan.enabled:
        scan_result = run_scan_pipeline(params, forward_result)
        paths = forward_result["paths"]
        confidence_metrics = build_confidence_metrics(
            params,
            scan_result,
            scan_result["scan_data"],
            params.derived.time_axis,
            forward_result["source_xyz"],
            forward_result["receiver_xyz"],
            forward_result["velocity_model"],
        )
        if params.output.save_arrays:
            save_json(paths["arrays"] / "arr_confidence_metrics.json", confidence_metrics)
        if params.output.save_figures:
            plot_confidence_diagnostics(
                params,
                scan_result,
                confidence_metrics,
                paths["figures"] / "fig_confidence_diagnostics.png",
            )
            plot_y_high_score_width_check(
                params,
                scan_result,
                confidence_metrics,
                paths["figures"] / "fig_y_high_score_width_check.png",
            )
            plot_3d_high_score_uncertainty_summary(
                params,
                confidence_metrics["high_score_region"],
                paths["figures"] / "fig_3d_high_score_uncertainty_summary.png",
            )
            plot_x_y_depth_uncertainty_slices(
                params,
                scan_result["score_volume_active"],
                confidence_metrics["high_score_region"],
                confidence_metrics["recommended_location"],
                paths["figures"] / "fig_x_y_depth_uncertainty_slices.png",
            )
            plot_multi_attribute_score_comparison(
                params,
                scan_result,
                paths["figures"] / "fig_multi_attribute_score_comparison.png",
            )
        if params.output.save_report:
            write_confidence_report(params, paths["reports"] / "report_confidence.md", confidence_metrics)

        if params.scan.compare_score_methods:
            score_method_comparison = run_score_method_comparison(
                scan_result["scan_data"],
                params.derived.time_axis,
                forward_result["source_xyz"],
                forward_result["receiver_xyz"],
                forward_result["velocity_model"],
                build_scan_grid(params),
                params,
            )
            if params.output.save_arrays:
                for method, method_result in score_method_comparison["methods"].items():
                    np.save(
                        paths["arrays"] / f"arr_score_volume_unweighted_{method}.npy",
                        method_result["score_volume_unweighted"],
                    )
            if params.output.save_figures:
                plot_score_method_depth_comparison(
                    params,
                    score_method_comparison,
                    paths["figures"] / "fig_score_method_depth_comparison.png",
                )
            if params.output.save_report:
                _write_score_method_comparison_report(
                    params,
                    paths["reports"] / "report_score_method_comparison.md",
                    score_method_comparison,
                )

        if params.scan.depth_prior_sensitivity_enabled:
            depth_prior_sensitivity = run_depth_prior_sensitivity(scan_result["score_volume_unweighted"], params)
            if params.output.save_figures:
                plot_depth_prior_sensitivity(
                    params,
                    depth_prior_sensitivity,
                    paths["figures"] / "fig_depth_prior_sensitivity.png",
                )
            if params.output.save_report:
                _write_depth_prior_sensitivity_report(
                    paths["reports"] / "report_depth_prior_sensitivity.md",
                    depth_prior_sensitivity,
                )

        truth_xyz = np.array([params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m], dtype=float)
        truth_diffraction_times = compute_candidate_diffraction_times(
            truth_xyz,
            forward_result["source_xyz"],
            forward_result["receiver_xyz"],
            forward_result["velocity_model"],
            t0_s=params.time.t0_s,
        )

        if params.preprocessing.ablation_enabled:
            preprocessing_ablation = run_preprocessing_ablation(
                params,
                forward_result["synthetic_data"],
                scan_result["direct_times"],
                forward_result["source_xyz"],
                forward_result["receiver_xyz"],
                forward_result["velocity_model"],
            )
            if params.output.save_figures:
                plot_preprocessing_ablation_summary(
                    preprocessing_ablation,
                    paths["figures"] / "fig_preprocessing_ablation_summary.png",
                )
            if params.output.save_report:
                write_preprocessing_ablation_report(
                    paths["reports"] / "report_preprocessing_ablation.md",
                    preprocessing_ablation,
                )

        fk_validation = run_fk_filter_validation(
            params,
            scan_result["scan_data"],
            scan_result["direct_times"],
            truth_diffraction_times,
        )
        if params.output.save_figures:
            plot_fk_spectrum_before_after(
                params,
                scan_result["scan_data"],
                fk_validation["filtered_data"],
                paths["figures"] / "fig_fk_spectrum_before_after.png",
            )
            plot_fk_filter_effect_on_gather(
                params,
                scan_result["scan_data"],
                fk_validation["filtered_data"],
                paths["figures"] / "fig_fk_filter_effect_on_gather.png",
            )
        if params.output.save_report:
            write_fk_filter_validation_report(paths["reports"] / "report_fk_filter_validation.md", fk_validation)

        attribute_volumes = scan_result.get("attribute_score_volumes", {})
        if params.output.save_figures:
            if "matched_wavelet_score" in attribute_volumes:
                plot_matched_wavelet_score_comparison(
                    params,
                    attribute_volumes["matched_wavelet_score"],
                    paths["figures"] / "fig_matched_wavelet_score_comparison.png",
                )
            if "semblance_score" in attribute_volumes:
                plot_semblance_score_volume_slice(
                    params,
                    attribute_volumes["semblance_score"],
                    paths["figures"] / "fig_semblance_score_volume_slice.png",
                )
            if "frequency_shift_score" in attribute_volumes:
                plot_frequency_shift_attribute(
                    params,
                    attribute_volumes["frequency_shift_score"],
                    paths["figures"] / "fig_frequency_shift_attribute.png",
                )
            plot_3d_high_score_components(
                confidence_metrics["high_score_region"],
                paths["figures"] / "fig_3d_high_score_components.png",
            )
            plot_recommendation_decision_flow(
                confidence_metrics,
                paths["figures"] / "fig_recommendation_decision_flow.png",
            )
        if params.output.save_report:
            if "matched_wavelet_score" in attribute_volumes:
                write_attribute_validation_report(
                    paths["reports"] / "report_matched_wavelet_validation.md",
                    "matched wavelet score 验证报告",
                    summarize_volume(params, attribute_volumes["matched_wavelet_score"]),
                    "matched wavelet 使用 Ricker 模板归一化相关。若它未优于 energy，应说明当前模板匹配仍需调参或更真实子波。",
                )
            if "semblance_score" in attribute_volumes:
                write_attribute_validation_report(
                    paths["reports"] / "report_semblance_validation.md",
                    "semblance score 验证报告",
                    summarize_volume(params, attribute_volumes["semblance_score"]),
                    "semblance 衡量沿理论绕射曲线对齐后的多炮多道波形一致性。",
                )
            if "frequency_shift_score" in attribute_volumes:
                write_attribute_validation_report(
                    paths["reports"] / "report_frequency_shift_attribute.md",
                    "frequency shift attribute 验证报告",
                    summarize_volume(params, attribute_volumes["frequency_shift_score"]),
                    "frequency shift 仅是谱质心下降诊断，默认权重为 0，不支配主定位。",
                )

        if params.scan.multi_attribute_ablation_enabled:
            multi_attribute_ablation = run_multi_attribute_ablation(params, scan_result)
            if params.output.save_arrays:
                for group_name, volume in multi_attribute_ablation["volumes"].items():
                    np.save(paths["arrays"] / f"arr_score_volume_multi_attribute_ablation_{group_name}.npy", volume)
            if params.output.save_figures:
                plot_multi_attribute_ablation(
                    multi_attribute_ablation,
                    paths["figures"] / "fig_multi_attribute_ablation.png",
                )
            if params.output.save_report:
                write_multi_attribute_ablation_report(
                    paths["reports"] / "report_multi_attribute_ablation.md",
                    multi_attribute_ablation,
                )

        if params.scan.geometry_ablation_enabled:
            geometry_ablation = run_geometry_ablation(
                params,
                forward_result["source_xyz"],
                forward_result["receiver_xyz"],
                forward_result["scatter_xyz"],
                forward_result["scatter_weight"],
                forward_result["velocity_model"],
            )
            if params.output.save_figures:
                plot_geometry_ablation_best_locations(
                    params,
                    geometry_ablation,
                    paths["figures"] / "fig_geometry_ablation_best_locations.png",
                )
                plot_geometry_ablation_uncertainty_spans(
                    geometry_ablation,
                    paths["figures"] / "fig_geometry_ablation_uncertainty_spans.png",
                )
            if params.output.save_report:
                write_geometry_ablation_report(paths["reports"] / "report_geometry_ablation.md", geometry_ablation)

        if params.scan.velocity_ablation_enabled:
            velocity_model_ablation = run_velocity_model_ablation(
                params,
                forward_result["source_xyz"],
                forward_result["receiver_xyz"],
                forward_result["scatter_xyz"],
                forward_result["scatter_weight"],
            )
            model_mismatch = run_model_mismatch_experiment(
                params,
                forward_result["source_xyz"],
                forward_result["receiver_xyz"],
                forward_result["scatter_xyz"],
                forward_result["scatter_weight"],
            )
            if params.output.save_figures:
                plot_layered_velocity_profile(params, paths["figures"] / "fig_layered_velocity_profile.png")
                plot_velocity_model_comparison(
                    velocity_model_ablation,
                    paths["figures"] / "fig_velocity_model_comparison.png",
                )
                plot_velocity_model_travel_time_residuals(
                    velocity_model_ablation,
                    paths["figures"] / "fig_velocity_model_travel_time_residuals.png",
                )
                plot_model_mismatch_error_summary(
                    model_mismatch,
                    paths["figures"] / "fig_model_mismatch_error_summary.png",
                )
            if params.output.save_report:
                write_velocity_model_ablation_report(
                    paths["reports"] / "report_velocity_model_ablation.md",
                    velocity_model_ablation,
                )
                write_model_mismatch_report(paths["reports"] / "report_model_mismatch.md", model_mismatch)

        _write_full_pipeline_report(
            params,
            forward_result["paths"]["reports"] / "report_full_pipeline.md",
            scan_result,
            confidence_metrics,
        )
        latest_stable_path = Path(params.derived.latest_stable_dir)
        stage4b_validation = {
            "preprocessing_ablation": preprocessing_ablation,
            "fk_filter_validation": {
                key: value
                for key, value in (fk_validation or {}).items()
                if key != "filtered_data"
            },
            "multi_attribute_ablation": {
                key: value
                for key, value in (multi_attribute_ablation or {}).items()
                if key != "volumes"
            },
            "geometry_ablation": geometry_ablation,
        }
        stage5a_validation = {
            "velocity_model_ablation": velocity_model_ablation,
            "model_mismatch": model_mismatch,
        }
        _build_final_metadata(
            params,
            forward_result,
            scan_result,
            confidence_metrics,
            score_method_comparison,
            depth_prior_sensitivity,
            stage4b_validation,
            stage5a_validation,
            latest_stable_path if params.output.export_latest_stable else None,
            bool(params.output.export_latest_stable),
        )
        if params.output.export_latest_stable:
            summary_info = {
                "commit_id": get_git_commit_id(Path.cwd()),
                "task_name": "Stage 5A 项目收口清理 + 稳定算法沉淀 + 分层/非均匀速度模型",
                "run_time": datetime.now().isoformat(timespec="seconds"),
                "source_run_dir": str(forward_result["paths"]["root"]),
                "best_location": scan_result["best_location"],
                "raw_best_location": scan_result["raw_best_location"],
                "unweighted_best_location": scan_result["unweighted_best_location"],
                "weighted_best_location": scan_result["weighted_best_location"],
                "raw_weighted_difference": scan_result["raw_weighted_difference"],
                "truth_error": scan_result["truth_error"],
                "confidence": confidence_metrics,
                "score_method_comparison": score_method_comparison,
                "depth_prior_sensitivity": depth_prior_sensitivity,
                "stage4b_validation": stage4b_validation,
                "stage5a_validation": stage5a_validation,
            }
            stable_export_info = export_latest_stable_outputs(
                forward_result["paths"]["root"],
                latest_stable_path,
                summary_info,
            )
    else:
        (forward_result["paths"]["reports"] / "report_full_pipeline.md").write_text(
            "本次 full_pipeline 关闭了 scan_enabled，因此只完成正演和伪波场输出。\n",
            encoding="utf-8",
        )

    result = dict(forward_result)
    result["scan_result"] = scan_result
    result["confidence_metrics"] = confidence_metrics
    result["score_method_comparison"] = score_method_comparison
    result["depth_prior_sensitivity"] = depth_prior_sensitivity
    result["preprocessing_ablation"] = preprocessing_ablation
    result["fk_validation"] = fk_validation
    result["multi_attribute_ablation"] = multi_attribute_ablation
    result["geometry_ablation"] = geometry_ablation
    result["velocity_model_ablation"] = velocity_model_ablation
    result["model_mismatch"] = model_mismatch
    result["stable_export_info"] = stable_export_info
    return result
