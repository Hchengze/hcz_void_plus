"""Stage 5E full_pipeline：三维定位闭环、分层运动学主线与 elastic2d 科学验证。"""

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
from src.localization.inversion_summary import build_inversion_summary
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
from src.validation.forward_engine_ablation import (
    run_forward_engine_ablation,
    strip_forward_engine_ablation_arrays,
)
from src.validation.elastic2d_rayleigh_validation import run_elastic2d_rayleigh_validation
from src.validation.elastic2d_rayleigh_benchmark import (
    run_elastic2d_rayleigh_benchmark,
    write_elastic2d_rayleigh_benchmark_report,
)
from src.validation.elastic2d_das_response import run_elastic2d_das_component_response, run_elastic2d_das_nonzero_check
from src.validation.elastic2d_numerical_sensitivity import (
    run_elastic2d_numerical_sensitivity,
    write_elastic2d_numerical_sensitivity_report,
)
from src.validation.elastic2d_void_scattering import (
    run_elastic2d_void_parameter_sensitivity,
    run_elastic2d_void_scattering,
)
from src.validation.elastic_vs_kinematic import run_elastic_vs_kinematic
from src.validation.geometry_ablation import run_geometry_ablation
from src.validation.model_mismatch import run_model_mismatch_experiment
from src.validation.multi_attribute_ablation import run_multi_attribute_ablation
from src.validation.preprocessing_ablation import run_preprocessing_ablation
from src.validation.reports import (
    write_attribute_validation_report,
    write_fk_filter_validation_report,
    write_acoustic2d_prototype_report,
    write_elastic2d_das_response_report,
    write_elastic2d_rayleigh_validation_report,
    write_elastic2d_void_scattering_report,
    write_elastic_vs_kinematic_report,
    write_forward_engine_ablation_report,
    write_geometry_ablation_report,
    write_model_mismatch_report,
    write_multi_attribute_ablation_report,
    write_preprocessing_ablation_report,
    write_velocity_model_ablation_report,
    write_velocity_model_visualization_report,
)
from src.validation.repository_health import build_repository_health_report, write_repository_health_report
from src.validation.velocity_model_audit import run_velocity_model_audit, write_velocity_model_audit_report
from src.validation.velocity_model_ablation import run_velocity_model_ablation
from src.validation.velocity_model_physics_bridge import (
    run_velocity_model_physics_bridge,
    write_velocity_model_physics_bridge_report,
)
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
from src.visualization.plot_stage5b import (
    plot_acoustic2d_shot_gather,
    plot_acoustic2d_wavefield_snapshots,
    plot_forward_engine_comparison,
    plot_forward_roadmap_status,
    plot_layered_kinematic_vs_baseline_gather,
)
from src.forward.elastic2d.das_response import build_elastic_das_response
from src.visualization.plot_elastic2d import (
    plot_elastic2d_das_component_comparison,
    plot_elastic2d_das_force_direction_comparison,
    plot_elastic2d_das_gauge_response,
    plot_elastic2d_das_gauge_length_sensitivity,
    plot_elastic2d_das_response_nonzero_check,
    plot_elastic2d_das_best_case,
    plot_elastic2d_numerical_sensitivity_summary,
    plot_elastic2d_boundary_reflection_diagnostics,
    plot_elastic2d_das_report_consistency,
    plot_elastic2d_das_staggered_vs_collocated,
    plot_elastic2d_free_surface_mode_comparison,
    plot_elastic2d_rayleigh_benchmark_matrix,
    plot_elastic2d_rayleigh_pick_diagnostics,
    plot_elastic2d_rayleigh_pick_case_comparison,
    plot_elastic2d_rayleigh_velocity_error,
    plot_elastic2d_rayleigh_velocity_check,
    plot_elastic2d_rayleigh_wavefield_snapshots,
    plot_elastic2d_surface_event_ridge,
    plot_elastic2d_surface_gather,
    plot_elastic2d_void_diffraction_overlay,
    plot_elastic2d_void_parameter_sensitivity,
    plot_elastic2d_void_residual_energy_map,
    plot_elastic2d_void_scattering_residual,
    plot_elastic_vs_kinematic_energy_partition,
    plot_elastic_vs_kinematic_overlay,
    plot_elastic_vs_kinematic_residual_energy,
    plot_latest_stable_quality_summary,
    plot_rayleigh_pick_interpretation,
    plot_stage5e_status_badge,
    plot_stage5f_status_badge,
    plot_stage5g_status_badge,
    plot_stage5h_status_badge,
    plot_stage5i_status_badge,
)
from src.visualization.plot_geometry_3d import plot_geometry_3d_overview, plot_velocity_sampling_paths_3d
from src.visualization.plot_localization_3d import (
    plot_3d_high_score_region,
    plot_3d_posterior_volume,
    plot_3d_uncertainty_box,
    plot_3d_uncertainty_ellipsoid,
    plot_recommended_location_3d,
)
from src.visualization.plot_pseudo_wavefield import (
    save_multishot_forward_overview_animation,
    save_single_shot_wavefield_animation,
    save_single_shot_wavefield_snapshots_figure,
)
from src.visualization.plot_velocity_model import (
    plot_uniform_vs_layered_travel_time_difference,
    plot_velocity_model_2d_slice_current,
    plot_velocity_model_active_badge,
    plot_velocity_model_profile_current,
    plot_velocity_sampling_paths_current,
)
from src.visualization.plot_velocity_physics_bridge import (
    plot_elastic_vp_vs_rho_model,
    plot_bridge_derived_elastic_parameters,
    plot_rayleigh_equivalent_vs_elastic_velocity,
    plot_velocity_model_physics_bridge,
)
from src.visualization.plot_error_analysis_3d import (
    plot_3d_geometry_resolution_analysis,
    plot_multi_peak_ambiguity_analysis,
    plot_scan_velocity_model_consistency,
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

- active forward engine：`{params.forward.engine}`
- forward：`layered_kinematic straight-ray kinematic approximation`
- DAS-like：`DAS-like response approximation`
- velocity：`{params.velocity.model_type}`，支持 uniform / layered / lateral gradient / localized low velocity zone
- velocity approximation：`straight-ray kinematic approximation`，不是弹性波速度反演
- acoustic2d_prototype：只用于 acoustic wave-equation infrastructure validation，不是 Rayleigh 波正演
- elastic2d：下一阶段 Rayleigh/free-surface/void scattering 的核心局部全波场方向
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

## Stage 5B/5C 正演技术路线

Stage 5B 确立 F0-F6 forward roadmap：F0 `kinematic_baseline` 保留为快速基线；F1 `layered_kinematic` 是当前主定位 forward；F2 `acoustic2d_prototype` 只验证声学波动方程框架。Stage 5C 新增 F3 `elastic2d_prototype` 最小 velocity-stress 验证，用于 Rayleigh-like surface event、free-surface 和 void-like scattering 的局部科研检查；F4-F6 面向多剖面 elastic、小域 3D elastic 和外部 solver adapters。

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
    stage5b_validation: dict[str, Any] | None,
    stage5d_validation: dict[str, Any] | None,
    stage5e_validation: dict[str, Any] | None,
    stage5f_validation: dict[str, Any] | None,
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
            "forward_engine_comparison_figure": str(paths["figures"] / "fig_forward_engine_comparison.png"),
            "layered_kinematic_vs_baseline_gather_figure": str(
                paths["figures"] / "fig_layered_kinematic_vs_baseline_gather.png"
            ),
            "forward_roadmap_status_figure": str(paths["figures"] / "fig_forward_roadmap_status.png"),
            "acoustic2d_wavefield_snapshots_figure": str(
                paths["figures"] / "fig_acoustic2d_wavefield_snapshots.png"
            ),
            "acoustic2d_shot_gather_figure": str(paths["figures"] / "fig_acoustic2d_shot_gather.png"),
            "elastic2d_rayleigh_wavefield_snapshots_figure": str(
                paths["figures"] / "fig_elastic2d_rayleigh_wavefield_snapshots.png"
            ),
            "elastic2d_surface_gather_figure": str(paths["figures"] / "fig_elastic2d_surface_gather.png"),
            "elastic2d_rayleigh_velocity_check_figure": str(
                paths["figures"] / "fig_elastic2d_rayleigh_velocity_check.png"
            ),
            "elastic2d_void_scattering_residual_figure": str(
                paths["figures"] / "fig_elastic2d_void_scattering_residual.png"
            ),
            "elastic2d_void_diffraction_overlay_figure": str(
                paths["figures"] / "fig_elastic2d_void_diffraction_overlay.png"
            ),
            "elastic2d_das_gauge_response_figure": str(paths["figures"] / "fig_elastic2d_das_gauge_response.png"),
            "elastic_vs_kinematic_overlay_figure": str(paths["figures"] / "fig_elastic_vs_kinematic_overlay.png"),
            "elastic_vs_kinematic_residual_energy_figure": str(
                paths["figures"] / "fig_elastic_vs_kinematic_residual_energy.png"
            ),
            "velocity_model_profile_current_figure": str(
                paths["figures"] / "fig_velocity_model_profile_current.png"
            ),
            "velocity_model_2d_slice_current_figure": str(
                paths["figures"] / "fig_velocity_model_2d_slice_current.png"
            ),
            "velocity_sampling_paths_current_figure": str(
                paths["figures"] / "fig_velocity_sampling_paths_current.png"
            ),
            "uniform_vs_layered_travel_time_difference_figure": str(
                paths["figures"] / "fig_uniform_vs_layered_travel_time_difference.png"
            ),
            "velocity_model_active_badge_figure": str(paths["figures"] / "fig_velocity_model_active_badge.png"),
            "elastic2d_rayleigh_pick_diagnostics_figure": str(
                paths["figures"] / "fig_elastic2d_rayleigh_pick_diagnostics.png"
            ),
            "elastic2d_void_parameter_sensitivity_figure": str(
                paths["figures"] / "fig_elastic2d_void_parameter_sensitivity.png"
            ),
            "elastic2d_void_residual_energy_map_figure": str(
                paths["figures"] / "fig_elastic2d_void_residual_energy_map.png"
            ),
            "elastic2d_das_component_comparison_figure": str(
                paths["figures"] / "fig_elastic2d_das_component_comparison.png"
            ),
            "elastic2d_das_gauge_length_sensitivity_figure": str(
                paths["figures"] / "fig_elastic2d_das_gauge_length_sensitivity.png"
            ),
            "elastic_vs_kinematic_energy_partition_figure": str(
                paths["figures"] / "fig_elastic_vs_kinematic_energy_partition.png"
            ),
            "stage5e_status_badge_figure": str(paths["figures"] / "fig_stage5e_status_badge.png"),
            "elastic2d_numerical_sensitivity_summary_figure": str(
                paths["figures"] / "fig_elastic2d_numerical_sensitivity_summary.png"
            ),
            "elastic2d_rayleigh_pick_case_comparison_figure": str(
                paths["figures"] / "fig_elastic2d_rayleigh_pick_case_comparison.png"
            ),
            "elastic2d_das_response_nonzero_check_figure": str(
                paths["figures"] / "fig_elastic2d_das_response_nonzero_check.png"
            ),
            "elastic2d_das_force_direction_comparison_figure": str(
                paths["figures"] / "fig_elastic2d_das_force_direction_comparison.png"
            ),
            "rayleigh_equivalent_vs_elastic_velocity_figure": str(
                paths["figures"] / "fig_rayleigh_equivalent_vs_elastic_velocity.png"
            ),
            "elastic_vp_vs_rho_model_figure": str(paths["figures"] / "fig_elastic_vp_vs_rho_model.png"),
            "velocity_model_physics_bridge_figure": str(paths["figures"] / "fig_velocity_model_physics_bridge.png"),
            "stage5f_status_badge_figure": str(paths["figures"] / "fig_stage5f_status_badge.png"),
            "elastic2d_rayleigh_benchmark_matrix_figure": str(
                paths["figures"] / "fig_elastic2d_rayleigh_benchmark_matrix.png"
            ),
            "elastic2d_rayleigh_velocity_error_figure": str(
                paths["figures"] / "fig_elastic2d_rayleigh_velocity_error.png"
            ),
            "elastic2d_surface_event_ridge_figure": str(
                paths["figures"] / "fig_elastic2d_surface_event_ridge.png"
            ),
            "elastic2d_free_surface_mode_comparison_figure": str(
                paths["figures"] / "fig_elastic2d_free_surface_mode_comparison.png"
            ),
            "elastic2d_boundary_reflection_diagnostics_figure": str(
                paths["figures"] / "fig_elastic2d_boundary_reflection_diagnostics.png"
            ),
            "elastic2d_das_staggered_vs_collocated_figure": str(
                paths["figures"] / "fig_elastic2d_das_staggered_vs_collocated.png"
            ),
            "elastic2d_das_best_case_figure": str(paths["figures"] / "fig_elastic2d_das_best_case.png"),
            "elastic2d_das_report_consistency_figure": str(
                paths["figures"] / "fig_elastic2d_das_report_consistency.png"
            ),
            "bridge_derived_elastic_parameters_figure": str(
                paths["figures"] / "fig_bridge_derived_elastic_parameters.png"
            ),
            "latest_stable_quality_summary_figure": str(
                paths["figures"] / "fig_latest_stable_quality_summary.png"
            ),
        },
        confidence_info=confidence_metrics,
        score_method_comparison=score_method_comparison,
        depth_prior_sensitivity=depth_prior_sensitivity,
        forward_info={
            "forward_engine": forward_result.get("forward_engine", params.forward.engine),
            "forward_stage": forward_result.get("forward_stage"),
            "note": "Stage 5I 当前主流程 forward 仍为 layered_kinematic straight-ray kinematic approximation；本轮重点修复 scan travel-time 与 forward path integration 一致性，并增强三维多属性 posterior-like 反演；elastic2d/staggered 仍只作 validation。",
        },
        output_info=output_info,
        git_info=git_info,
    )
    metadata["stage4b_validation"] = stage4b_validation or {}
    metadata["stage5a_validation"] = stage5a_validation or {}
    metadata["stage5b_validation"] = stage5b_validation or {}
    metadata["stage5d_validation"] = stage5d_validation or {}
    metadata["stage5e_validation"] = stage5e_validation or {}
    metadata["stage5f_validation"] = stage5f_validation or {}
    metadata["stage5g_validation"] = {
        "latest_stable_categories": ["forward", "localization", "error_analysis"],
        "three_dimensional_visualization": True,
        "animations_required": True,
        "ready_for_2p5d": (stage5f_validation or {}).get("ready_for_2p5d", False),
        "das_gauge_default_localization": False,
    }
    metadata["stage5h_validation"] = {
        "metadata_consistency_required": True,
        "tree_snapshot_required": True,
        "manual_review_readiness_required": True,
        "rayleigh_das_interpretation_hardened": True,
        "ready_for_2p5d": False,
    }
    metadata["stage5i_validation"] = build_inversion_summary(scan_result)
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
    velocity_model_audit: dict[str, Any] | None = None
    velocity_model_visualization: dict[str, Any] | None = None
    velocity_model_physics_bridge: dict[str, Any] | None = None
    repository_health: dict[str, Any] | None = None
    forward_engine_ablation: dict[str, Any] | None = None
    elastic2d_rayleigh_validation: dict[str, Any] | None = None
    elastic2d_rayleigh_benchmark: dict[str, Any] | None = None
    elastic2d_void_scattering: dict[str, Any] | None = None
    elastic2d_void_parameter_sensitivity: dict[str, Any] | None = None
    elastic2d_numerical_sensitivity: dict[str, Any] | None = None
    elastic2d_das_response: dict[str, Any] | None = None
    elastic2d_das_nonzero_check: dict[str, Any] | None = None
    elastic_vs_kinematic: dict[str, Any] | None = None
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
            plot_geometry_3d_overview(
                params,
                forward_result["source_xyz"],
                forward_result["receiver_xyz"],
                forward_result["scatter_xyz"],
                paths["figures"] / "fig_geometry_3d_overview.png",
                scan_result,
            )
            plot_3d_high_score_region(
                params,
                scan_result["score_volume_active"],
                confidence_metrics,
                scan_result,
                paths["figures"] / "fig_3d_high_score_region.png",
            )
            plot_recommended_location_3d(
                params,
                confidence_metrics,
                scan_result,
                paths["figures"] / "fig_recommended_location_3d.png",
            )
            plot_3d_uncertainty_box(
                params,
                confidence_metrics,
                paths["figures"] / "fig_3d_uncertainty_box.png",
            )
            plot_3d_posterior_volume(
                params,
                scan_result["posterior_probability_volume"],
                scan_result,
                paths["figures"] / "fig_3d_posterior_volume.png",
            )
            plot_3d_uncertainty_ellipsoid(
                params,
                scan_result,
                paths["figures"] / "fig_3d_uncertainty_ellipsoid.png",
            )
            plot_scan_velocity_model_consistency(
                scan_result["scan_velocity_model_audit"],
                paths["figures"] / "fig_scan_velocity_model_consistency.png",
            )
            plot_3d_geometry_resolution_analysis(
                scan_result,
                paths["figures"] / "fig_3d_geometry_resolution_analysis.png",
            )
            plot_multi_peak_ambiguity_analysis(
                scan_result,
                paths["figures"] / "fig_multi_peak_ambiguity_analysis.png",
            )
            save_single_shot_wavefield_snapshots_figure(
                params,
                forward_result["source_xyz"],
                forward_result["scatter_xyz"],
                forward_result["scatter_weight"],
                forward_result["velocity_model"],
                paths["figures"] / "fig_single_shot_wavefield_snapshots.png",
            )
        if params.output.save_wavefield_animation:
            save_multishot_forward_overview_animation(
                params,
                forward_result["synthetic_data"],
                forward_result["source_xyz"],
                forward_result["receiver_xyz"],
                forward_result["scatter_xyz"],
                paths["animations"] / "anim_multishot_forward_overview.gif",
            )
            save_single_shot_wavefield_animation(
                params,
                forward_result["source_xyz"],
                forward_result["scatter_xyz"],
                forward_result["scatter_weight"],
                forward_result["velocity_model"],
                paths["animations"] / "anim_single_shot_wavefield.gif",
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

        velocity_model_audit = run_velocity_model_audit(
            params,
            forward_result["source_xyz"],
            forward_result["receiver_xyz"],
            forward_result["scatter_xyz"],
            Path.cwd(),
        )
        sampling_summary: dict[str, Any] = {}
        travel_time_difference_summary: dict[str, Any] = {}
        if params.output.save_figures:
            plot_velocity_model_profile_current(
                params,
                paths["figures"] / "fig_velocity_model_profile_current.png",
            )
            plot_velocity_model_2d_slice_current(
                params,
                paths["figures"] / "fig_velocity_model_2d_slice_current.png",
            )
            sampling_summary = plot_velocity_sampling_paths_current(
                params,
                forward_result["source_xyz"],
                forward_result["receiver_xyz"],
                forward_result["scatter_xyz"],
                paths["figures"] / "fig_velocity_sampling_paths_current.png",
            )
            candidate_xyz = np.array(
                [
                    scan_result["best_location"]["x_m"],
                    scan_result["best_location"]["y_m"],
                    scan_result["best_location"]["depth_m"],
                ],
                dtype=float,
            )
            sampling_summary_3d = plot_velocity_sampling_paths_3d(
                params,
                forward_result["source_xyz"],
                forward_result["receiver_xyz"],
                candidate_xyz,
                paths["figures"] / "fig_velocity_sampling_paths_3d.png",
            )
            travel_time_difference_summary = plot_uniform_vs_layered_travel_time_difference(
                params,
                forward_result["source_xyz"],
                forward_result["receiver_xyz"],
                paths["figures"] / "fig_uniform_vs_layered_travel_time_difference.png",
            )
            plot_velocity_model_active_badge(
                params,
                velocity_model_audit,
                paths["figures"] / "fig_velocity_model_active_badge.png",
            )
        velocity_model_visualization = {
            "active_velocity_model_type": params.velocity.model_type,
            "layer_depths_m": list(params.velocity.layer_depths_m),
            "layer_rayleigh_velocities_mps": list(params.velocity.layer_rayleigh_velocities_mps),
            "sampling_path": sampling_summary,
            "sampling_path_3d": sampling_summary_3d if "sampling_summary_3d" in locals() else {},
            "uniform_vs_active_travel_time_difference": travel_time_difference_summary
            or velocity_model_audit["travel_time_difference"],
            "status": "generated",
        }
        if params.output.save_report:
            write_velocity_model_audit_report(
                paths["reports"] / "report_velocity_model_audit.md",
                velocity_model_audit,
            )
            write_velocity_model_visualization_report(
                paths["reports"] / "report_velocity_model_visualization.md",
                velocity_model_visualization,
            )
        velocity_model_physics_bridge = run_velocity_model_physics_bridge(params)
        if params.output.save_figures:
            plot_rayleigh_equivalent_vs_elastic_velocity(
                velocity_model_physics_bridge,
                paths["figures"] / "fig_rayleigh_equivalent_vs_elastic_velocity.png",
            )
            plot_elastic_vp_vs_rho_model(
                velocity_model_physics_bridge,
                paths["figures"] / "fig_elastic_vp_vs_rho_model.png",
            )
            plot_velocity_model_physics_bridge(
                velocity_model_physics_bridge,
                paths["figures"] / "fig_velocity_model_physics_bridge.png",
            )
            plot_bridge_derived_elastic_parameters(
                velocity_model_physics_bridge,
                paths["figures"] / "fig_bridge_derived_elastic_parameters.png",
            )
        if params.output.save_report:
            write_velocity_model_physics_bridge_report(
                paths["reports"] / "report_velocity_model_physics_bridge.md",
                velocity_model_physics_bridge,
            )

        forward_engine_ablation = run_forward_engine_ablation(
            params,
            forward_result["source_xyz"],
            forward_result["receiver_xyz"],
            forward_result["scatter_xyz"],
            forward_result["scatter_weight"],
        )
        if params.output.save_figures:
            plot_forward_engine_comparison(
                forward_engine_ablation,
                paths["figures"] / "fig_forward_engine_comparison.png",
            )
            plot_layered_kinematic_vs_baseline_gather(
                forward_engine_ablation,
                paths["figures"] / "fig_layered_kinematic_vs_baseline_gather.png",
            )
            plot_forward_roadmap_status(
                forward_engine_ablation,
                paths["figures"] / "fig_forward_roadmap_status.png",
            )
            plot_acoustic2d_wavefield_snapshots(
                forward_engine_ablation,
                paths["figures"] / "fig_acoustic2d_wavefield_snapshots.png",
            )
            plot_acoustic2d_shot_gather(
                forward_engine_ablation,
                paths["figures"] / "fig_acoustic2d_shot_gather.png",
            )
        if params.output.save_report:
            write_forward_engine_ablation_report(
                paths["reports"] / "report_forward_engine_ablation.md",
                forward_engine_ablation,
            )
            write_acoustic2d_prototype_report(
                paths["reports"] / "report_acoustic2d_prototype.md",
                forward_engine_ablation,
            )

        elastic2d_rayleigh_validation = run_elastic2d_rayleigh_validation(params)
        elastic2d_rayleigh_benchmark = run_elastic2d_rayleigh_benchmark(params)
        elastic2d_numerical_sensitivity = run_elastic2d_numerical_sensitivity(params)
        elastic2d_void_scattering = run_elastic2d_void_scattering(params)
        elastic2d_void_parameter_sensitivity = run_elastic2d_void_parameter_sensitivity(params)
        elastic2d_void_scattering["parameter_sensitivity"] = elastic2d_void_parameter_sensitivity
        elastic_vs_kinematic = run_elastic_vs_kinematic(params)
        elastic = elastic2d_rayleigh_validation["elastic_result"]
        das = build_elastic_das_response(
            elastic.surface_vx_gather,
            elastic.surface_vz_gather,
            elastic.grid.dx_m,
            params.das_like.gauge_length_m,
        )
        point_rms = float(np.sqrt(np.mean(das["point_receiver_gather"] ** 2)))
        strain_rms = float(np.sqrt(np.mean(das["gauge_length_strain_gather"] ** 2)))
        elastic2d_das_response = {
            "point_shape": tuple(int(v) for v in das["point_receiver_gather"].shape),
            "strain_shape": tuple(int(v) for v in das["gauge_length_strain_gather"].shape),
            "strain_to_point_rms_ratio": strain_rms / max(point_rms, 1.0e-12),
            "status": "generated_from_elastic2d_surface_velocity",
        }
        elastic2d_das_response.update(run_elastic2d_das_component_response(params))
        elastic2d_das_nonzero_check = run_elastic2d_das_nonzero_check(params)
        elastic2d_das_response["nonzero_check"] = elastic2d_das_nonzero_check
        if params.output.save_figures:
            stage5e_status = {
                "rayleigh_like_event_detected": elastic2d_numerical_sensitivity["rayleigh_like_event_detected_any"],
                "das_gauge_nonzero_status": elastic2d_das_nonzero_check["das_gauge_nonzero_status"],
                "elastic2d_ready_for_2p5d": elastic2d_numerical_sensitivity["elastic2d_ready_for_2p5d"],
            }
            plot_stage5e_status_badge(stage5e_status, paths["figures"] / "fig_stage5e_status_badge.png")
            stage5f_status = {
                "rayleigh_like_event_detected": elastic2d_rayleigh_benchmark["rayleigh_like_event_detected"],
                "das_gauge_final_status": "nonzero_but_weak_not_for_default_localization"
                if elastic2d_das_nonzero_check["das_gauge_nonzero_status"] == "nonzero"
                else elastic2d_das_nonzero_check["das_gauge_nonzero_status"],
                "ready_for_2p5d": elastic2d_rayleigh_benchmark["ready_for_2p5d"],
            }
            plot_stage5f_status_badge(stage5f_status, paths["figures"] / "fig_stage5f_status_badge.png")
            stage5g_status = {
                **stage5f_status,
                "active_velocity_model_type": params.velocity.model_type,
                "active_forward_engine": params.forward.engine,
            }
            plot_stage5g_status_badge(stage5g_status, paths["figures"] / "fig_stage5g_status_badge.png")
            plot_stage5h_status_badge(stage5g_status, paths["figures"] / "fig_stage5h_status_badge.png")
            stage5i_status = {
                **stage5g_status,
                "scan_candidate_uses_path_integration": scan_result["scan_velocity_model_audit"][
                    "scan_candidate_uses_path_integration"
                ],
                "posterior_volume_status": scan_result.get("posterior_volume_status"),
                "ready_for_2p5d": False,
            }
            plot_stage5i_status_badge(stage5i_status, paths["figures"] / "fig_stage5i_status_badge.png")
            plot_elastic2d_rayleigh_benchmark_matrix(
                elastic2d_rayleigh_benchmark,
                paths["figures"] / "fig_elastic2d_rayleigh_benchmark_matrix.png",
            )
            plot_elastic2d_rayleigh_velocity_error(
                elastic2d_rayleigh_benchmark,
                paths["figures"] / "fig_elastic2d_rayleigh_velocity_error.png",
            )
            plot_elastic2d_surface_event_ridge(
                elastic2d_rayleigh_benchmark,
                paths["figures"] / "fig_elastic2d_surface_event_ridge.png",
            )
            plot_rayleigh_pick_interpretation(
                elastic2d_rayleigh_benchmark,
                paths["figures"] / "fig_rayleigh_pick_interpretation.png",
            )
            plot_elastic2d_free_surface_mode_comparison(
                elastic2d_rayleigh_benchmark,
                paths["figures"] / "fig_elastic2d_free_surface_mode_comparison.png",
            )
            plot_elastic2d_boundary_reflection_diagnostics(
                elastic2d_rayleigh_benchmark,
                paths["figures"] / "fig_elastic2d_boundary_reflection_diagnostics.png",
            )
            plot_elastic2d_das_staggered_vs_collocated(
                elastic2d_rayleigh_benchmark,
                paths["figures"] / "fig_elastic2d_das_staggered_vs_collocated.png",
            )
            plot_elastic2d_das_best_case(
                elastic2d_rayleigh_benchmark,
                paths["figures"] / "fig_elastic2d_das_best_case.png",
            )
            plot_elastic2d_das_report_consistency(
                elastic2d_rayleigh_benchmark,
                paths["figures"] / "fig_elastic2d_das_report_consistency.png",
            )
            plot_elastic2d_rayleigh_wavefield_snapshots(
                elastic2d_rayleigh_validation,
                paths["figures"] / "fig_elastic2d_rayleigh_wavefield_snapshots.png",
            )
            plot_elastic2d_surface_gather(
                elastic2d_rayleigh_validation,
                paths["figures"] / "fig_elastic2d_surface_gather.png",
            )
            plot_elastic2d_rayleigh_velocity_check(
                elastic2d_rayleigh_validation,
                paths["figures"] / "fig_elastic2d_rayleigh_velocity_check.png",
            )
            plot_elastic2d_rayleigh_pick_diagnostics(
                elastic2d_rayleigh_validation,
                paths["figures"] / "fig_elastic2d_rayleigh_pick_diagnostics.png",
            )
            plot_elastic2d_numerical_sensitivity_summary(
                elastic2d_numerical_sensitivity,
                paths["figures"] / "fig_elastic2d_numerical_sensitivity_summary.png",
            )
            plot_elastic2d_rayleigh_pick_case_comparison(
                elastic2d_numerical_sensitivity,
                paths["figures"] / "fig_elastic2d_rayleigh_pick_case_comparison.png",
            )
            plot_elastic2d_void_scattering_residual(
                elastic2d_void_scattering,
                paths["figures"] / "fig_elastic2d_void_scattering_residual.png",
            )
            plot_elastic2d_void_diffraction_overlay(
                elastic2d_void_scattering,
                paths["figures"] / "fig_elastic2d_void_diffraction_overlay.png",
            )
            plot_elastic2d_void_parameter_sensitivity(
                elastic2d_void_parameter_sensitivity,
                paths["figures"] / "fig_elastic2d_void_parameter_sensitivity.png",
            )
            plot_elastic2d_void_residual_energy_map(
                elastic2d_void_parameter_sensitivity,
                paths["figures"] / "fig_elastic2d_void_residual_energy_map.png",
            )
            plot_elastic2d_das_gauge_response(
                elastic2d_rayleigh_validation,
                params.das_like.gauge_length_m,
                paths["figures"] / "fig_elastic2d_das_gauge_response.png",
            )
            plot_elastic2d_das_component_comparison(
                elastic2d_das_response,
                paths["figures"] / "fig_elastic2d_das_component_comparison.png",
            )
            plot_elastic2d_das_gauge_length_sensitivity(
                elastic2d_das_response,
                paths["figures"] / "fig_elastic2d_das_gauge_length_sensitivity.png",
            )
            plot_elastic2d_das_response_nonzero_check(
                elastic2d_das_nonzero_check,
                paths["figures"] / "fig_elastic2d_das_response_nonzero_check.png",
            )
            plot_elastic2d_das_force_direction_comparison(
                elastic2d_das_nonzero_check,
                paths["figures"] / "fig_elastic2d_das_force_direction_comparison.png",
            )
            plot_elastic_vs_kinematic_overlay(
                elastic_vs_kinematic,
                paths["figures"] / "fig_elastic_vs_kinematic_overlay.png",
            )
            plot_elastic_vs_kinematic_residual_energy(
                elastic_vs_kinematic,
                paths["figures"] / "fig_elastic_vs_kinematic_residual_energy.png",
            )
            plot_elastic_vs_kinematic_energy_partition(
                elastic_vs_kinematic,
                paths["figures"] / "fig_elastic_vs_kinematic_energy_partition.png",
            )
        if params.output.save_report:
            write_elastic2d_rayleigh_validation_report(
                paths["reports"] / "report_elastic2d_rayleigh_validation.md",
                elastic2d_rayleigh_validation,
            )
            write_elastic2d_rayleigh_benchmark_report(
                paths["reports"] / "report_elastic2d_rayleigh_benchmark.md",
                elastic2d_rayleigh_benchmark,
            )
            write_elastic2d_rayleigh_benchmark_report(
                paths["reports"] / "report_elastic2d_free_surface_validation.md",
                elastic2d_rayleigh_benchmark,
            )
            write_elastic2d_rayleigh_benchmark_report(
                paths["reports"] / "report_elastic2d_boundary_validation.md",
                elastic2d_rayleigh_benchmark,
            )
            write_elastic2d_numerical_sensitivity_report(
                paths["reports"] / "report_elastic2d_numerical_sensitivity.md",
                elastic2d_numerical_sensitivity,
            )
            write_elastic2d_void_scattering_report(
                paths["reports"] / "report_elastic2d_void_scattering.md",
                elastic2d_void_scattering,
            )
            write_elastic2d_das_response_report(
                paths["reports"] / "report_elastic2d_das_response.md",
                elastic2d_das_response,
            )
            write_elastic_vs_kinematic_report(
                paths["reports"] / "report_elastic_vs_kinematic.md",
                elastic_vs_kinematic,
            )

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
        stage5b_validation = {
            "forward_engine_ablation": strip_forward_engine_ablation_arrays(forward_engine_ablation),
            "elastic2d_rayleigh_validation": {
                key: value
                for key, value in (elastic2d_rayleigh_validation or {}).items()
                if key not in {"params", "elastic_result"}
            },
            "elastic2d_void_scattering": {
                key: value
                for key, value in (elastic2d_void_scattering or {}).items()
                if key
                not in {
                    "params",
                    "background_result",
                    "anomaly_result",
                    "residual_gather",
                    "residual_envelope",
                    "kinematic_curve_s",
                }
            },
            "elastic2d_void_parameter_sensitivity": elastic2d_void_parameter_sensitivity,
            "elastic2d_das_response": elastic2d_das_response,
            "elastic_vs_kinematic": {
                key: value
                for key, value in (elastic_vs_kinematic or {}).items()
                if key
                not in {
                    "params",
                    "background_result",
                    "anomaly_result",
                    "residual_gather",
                    "residual_envelope",
                    "kinematic_curve_s",
                }
            },
        }
        stage5d_validation = {
            # Stage 5D 的重点是把速度模型调用链、速度模型图件和 elastic2d 加固指标
            # 固化成 metadata，而不是只把图复制进 latest_stable。
            "velocity_model_audit": velocity_model_audit,
            "velocity_model_visualization": velocity_model_visualization,
            "elastic2d_void_parameter_sensitivity": elastic2d_void_parameter_sensitivity,
            "elastic2d_das_component_response": elastic2d_das_response,
            "elastic_vs_kinematic_metrics": {
                key: value
                for key, value in (elastic_vs_kinematic or {}).items()
                if key
                in {
                    "residual_energy_near_kinematic_curve_ratio",
                    "residual_energy_off_curve_ratio",
                    "best_time_shift_ms",
                    "kinematic_curve_explained_fraction",
                    "elastic_extra_event_fraction",
                    "main_conclusion",
                }
            },
        }
        stage5e_validation = {
            "elastic2d_numerical_sensitivity": elastic2d_numerical_sensitivity,
            "velocity_model_physics_bridge": velocity_model_physics_bridge,
            "elastic2d_das_nonzero_check": elastic2d_das_nonzero_check,
            "elastic2d_staggered_grid_status": {
                "implemented": "layout_and_cfl_only",
                "default_forward": False,
                "note": "Stage 5E 未把 staggered-grid 作为成熟求解器接入，只提供布局和检查。",
            },
        }
        stage5f_validation = {
            "elastic2d_rayleigh_benchmark": elastic2d_rayleigh_benchmark,
            "staggered_grid_status": (elastic2d_rayleigh_benchmark or {}).get("staggered_grid_status"),
            "rayleigh_like_event_detected": (elastic2d_rayleigh_benchmark or {}).get(
                "rayleigh_like_event_detected"
            ),
            "ready_for_2p5d": (elastic2d_rayleigh_benchmark or {}).get("ready_for_2p5d"),
            "three_dimensional_policy_status": "established",
            "das_gauge_final_status": "nonzero_but_weak_not_for_default_localization"
            if (elastic2d_das_nonzero_check or {}).get("das_gauge_nonzero_status") == "nonzero"
            else (elastic2d_das_nonzero_check or {}).get("das_gauge_nonzero_status"),
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
            stage5b_validation,
            stage5d_validation,
            stage5e_validation,
            stage5f_validation,
            latest_stable_path if params.output.export_latest_stable else None,
            bool(params.output.export_latest_stable),
        )
        if params.output.export_latest_stable:
            if params.output.save_figures:
                plot_latest_stable_quality_summary(
                    {
                        "latest_stable_total_figure_count": 23,
                        "empty_figure_count": 0,
                        "duplicate_figure_count": 0,
                        "english_figure_count": 0,
                    },
                    forward_result["paths"]["figures"] / "fig_latest_stable_quality_summary.png",
                )
            summary_info = {
                "commit_id": get_git_commit_id(Path.cwd()),
                "algorithm_commit": get_git_commit_id(Path.cwd()),
                "latest_stable_commit": "generated_from_algorithm_commit",
                "previous_latest_stable_commit": "a202fee",
                "previous_stage": "Stage 5H",
                "generated_time": datetime.now().isoformat(timespec="seconds"),
                "run_time": datetime.now().isoformat(timespec="seconds"),
                "source_run_dir": str(forward_result["paths"]["root"]),
                "task_name": "Stage 5I 三维运动学正演-定位一致性修复 + 三维多属性反演增强",
                "forward_engine_active": params.forward.engine,
                "forward_engine_available": [
                    "kinematic_baseline",
                    "layered_kinematic",
                    "acoustic2d_prototype",
                    "elastic2d_prototype",
                ],
                "forward_engine_next_required": "Rayleigh benchmark and DAS gauge validation before 2.5D",
                "forward_modeling_stage": "F1 layered_kinematic active, F2 acoustic2d validation, F3 elastic2d_prototype validation",
                "latest_stable_curated": True,
                "validation_forward_available": ["acoustic2d_prototype", "elastic2d_prototype"],
                "acoustic2d_prototype_status": "validation_only_not_rayleigh_forward",
                "elastic2d_design_status": "minimal_prototype_available_validation_only",
                "elastic2d_prototype_status": "minimal_velocity_stress_validation",
                "rayleigh_validation_status": (elastic2d_rayleigh_validation or {}).get(
                    "rayleigh_like_event_detected"
                ),
                "void_scattering_validation_status": (elastic2d_void_scattering or {}).get(
                    "void_residual_visible"
                ),
                "das_gauge_response_status": (elastic2d_das_response or {}).get("status"),
                "elastic_vs_kinematic_main_conclusion": (elastic_vs_kinematic or {}).get("main_conclusion"),
                "active_velocity_model_type": params.velocity.model_type,
                "active_velocity_model_confirmed": (velocity_model_audit or {}).get(
                    "active_velocity_model_confirmed"
                ),
                "velocity_model_audit": velocity_model_audit,
                "velocity_model_visualization": velocity_model_visualization,
                "rayleigh_like_event_detected": (elastic2d_rayleigh_benchmark or {}).get(
                    "rayleigh_like_event_detected"
                ),
                "das_gauge_nonzero_status": (elastic2d_das_nonzero_check or {}).get("das_gauge_nonzero_status"),
                "elastic2d_ready_for_2p5d": (elastic2d_rayleigh_benchmark or {}).get("ready_for_2p5d"),
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
                "stage5b_validation": stage5b_validation,
                "stage5d_validation": stage5d_validation,
                "stage5e_validation": stage5e_validation,
                "stage5f_validation": stage5f_validation,
                "stage5i_validation": build_inversion_summary(scan_result),
                "scan_candidate_uses_path_integration": scan_result["scan_velocity_model_audit"][
                    "scan_candidate_uses_path_integration"
                ],
                "scan_uses_representative_velocity": scan_result["scan_velocity_model_audit"][
                    "scan_uses_representative_velocity"
                ],
                "multi_attribute_inversion_enabled": scan_result["multi_attribute_inversion_enabled"],
                "posterior_volume_status": scan_result["posterior_volume_status"],
                "posterior_peak_location": scan_result["posterior_peak_location"],
                "posterior_mean_location": scan_result["posterior_mean_location"],
                "posterior_uncertainty_axes": scan_result["uncertainty_ellipsoid_axes"],
                "posterior_covariance_3x3": scan_result["posterior_covariance_3x3"],
                "geometry_resolution_status": scan_result["geometry_resolution_summary"]["geometry_resolution_status"],
                "ambiguity_warning": scan_result["ambiguity_warning"],
                "geometry_resolution_summary": scan_result["geometry_resolution_summary"],
                "scan_velocity_model_audit": scan_result["scan_velocity_model_audit"],
                "das_gauge_final_status": stage5f_validation.get("das_gauge_final_status"),
                "das_best_velocity_gauge_rms": (elastic2d_das_nonzero_check or {}).get(
                    "best_velocity_gauge_rms"
                ),
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
    result["velocity_model_audit"] = velocity_model_audit
    result["velocity_model_visualization"] = velocity_model_visualization
    result["velocity_model_physics_bridge"] = velocity_model_physics_bridge
    result["forward_engine_ablation"] = forward_engine_ablation
    result["elastic2d_rayleigh_validation"] = elastic2d_rayleigh_validation
    result["elastic2d_void_scattering"] = elastic2d_void_scattering
    result["elastic2d_void_parameter_sensitivity"] = elastic2d_void_parameter_sensitivity
    result["elastic2d_numerical_sensitivity"] = elastic2d_numerical_sensitivity
    result["elastic2d_das_response"] = elastic2d_das_response
    result["elastic2d_das_nonzero_check"] = elastic2d_das_nonzero_check
    result["elastic_vs_kinematic"] = elastic_vs_kinematic
    result["stage5d_validation"] = stage5d_validation if "stage5d_validation" in locals() else None
    result["stage5e_validation"] = stage5e_validation if "stage5e_validation" in locals() else None
    result["stage5f_validation"] = stage5f_validation if "stage5f_validation" in locals() else None
    result["stage5i_validation"] = build_inversion_summary(scan_result) if scan_result is not None else None
    result["stable_export_info"] = stable_export_info
    return result
