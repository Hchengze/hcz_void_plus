"""latest_stable 精选清单与图件元数据。

本模块只描述“哪些当前阶段成果允许进入 latest_stable”，不负责生成图件本身。
这样做的目的，是把 Stage 5D/5E 的图件自检从简单文件复制升级为可审计流程：
每张精选图都带有 stage、forward_engine 和 velocity_model_type 元数据，后续报告、
测试和人工复核可以据此判断是否混入旧阶段或错误主线图件。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StableFigureSpec:
    """latest_stable 图件条目。

    category:
        目标子目录，例如 core、forward、diagnostics。
    filename:
        时间戳运行目录 figures/ 下的图件文件名。
    required_report:
        与该图件最相关的报告相对路径。不是严格一图一报，但核心图必须能被报告
        或 summary 解释，避免“图生成了但没人知道它代表什么”。
    """

    category: str
    filename: str
    required_report: str


STAGE5F_FIGURE_SPECS: list[StableFigureSpec] = [
    StableFigureSpec("core", "fig_stage5f_status_badge.png", "reports/core/report_latest_stable_file_audit.md"),
    StableFigureSpec("core", "fig_geometry_layout_check.png", "reports/core/report_full_pipeline.md"),
    StableFigureSpec("core", "fig_shot_gather_000.png", "reports/core/report_full_pipeline.md"),
    StableFigureSpec("core", "fig_confidence_diagnostics.png", "reports/core/report_full_pipeline.md"),
    StableFigureSpec("core", "fig_forward_roadmap_status.png", "reports/forward/report_forward_engine_ablation.md"),
    StableFigureSpec("diagnostics", "fig_latest_stable_quality_summary.png", "reports/core/report_figure_quality_check.md"),
    StableFigureSpec("forward", "fig_elastic2d_rayleigh_benchmark_matrix.png", "reports/forward/report_elastic2d_rayleigh_benchmark.md"),
    StableFigureSpec("forward", "fig_elastic2d_rayleigh_velocity_error.png", "reports/forward/report_elastic2d_rayleigh_benchmark.md"),
    StableFigureSpec("forward", "fig_elastic2d_surface_event_ridge.png", "reports/forward/report_elastic2d_rayleigh_benchmark.md"),
    StableFigureSpec("forward", "fig_elastic2d_free_surface_mode_comparison.png", "reports/forward/report_elastic2d_free_surface_validation.md"),
    StableFigureSpec("forward", "fig_elastic2d_boundary_reflection_diagnostics.png", "reports/forward/report_elastic2d_boundary_validation.md"),
    StableFigureSpec(
        "forward",
        "fig_elastic2d_void_scattering_residual.png",
        "reports/forward/report_elastic2d_void_scattering.md",
    ),
    StableFigureSpec(
        "forward",
        "fig_elastic2d_das_staggered_vs_collocated.png",
        "reports/forward/report_elastic2d_das_response.md",
    ),
    StableFigureSpec(
        "forward",
        "fig_elastic2d_das_best_case.png",
        "reports/forward/report_elastic2d_das_response.md",
    ),
    StableFigureSpec(
        "forward",
        "fig_elastic2d_das_report_consistency.png",
        "reports/forward/report_elastic2d_das_response.md",
    ),
    StableFigureSpec("forward", "fig_elastic_vs_kinematic_energy_partition.png", "reports/forward/report_elastic2d_void_scattering.md"),
    StableFigureSpec("localization", "fig_scan_x_depth_slice.png", "reports/core/report_full_pipeline.md"),
    StableFigureSpec("localization", "fig_scan_x_y_slice.png", "reports/core/report_full_pipeline.md"),
    StableFigureSpec("localization", "fig_multi_attribute_ablation.png", "reports/localization/report_multi_attribute_ablation.md"),
    StableFigureSpec("uncertainty", "fig_3d_high_score_components.png", "reports/core/report_full_pipeline.md"),
    StableFigureSpec("uncertainty", "fig_x_y_depth_uncertainty_slices.png", "reports/core/report_full_pipeline.md"),
    StableFigureSpec("uncertainty", "fig_recommendation_decision_flow.png", "reports/core/report_full_pipeline.md"),
    StableFigureSpec("diagnostics", "fig_model_mismatch_error_summary.png", "reports/diagnostics/report_model_mismatch.md"),
    StableFigureSpec("diagnostics", "fig_depth_prior_sensitivity.png", "reports/core/report_full_pipeline.md"),
    StableFigureSpec(
        "diagnostics",
        "fig_velocity_model_profile_current.png",
        "reports/diagnostics/report_velocity_model_visualization.md",
    ),
    StableFigureSpec(
        "diagnostics",
        "fig_velocity_model_active_badge.png",
        "reports/diagnostics/report_velocity_model_audit.md",
    ),
    StableFigureSpec(
        "diagnostics",
        "fig_rayleigh_equivalent_vs_elastic_velocity.png",
        "reports/diagnostics/report_velocity_model_physics_bridge.md",
    ),
    StableFigureSpec(
        "diagnostics",
        "fig_bridge_derived_elastic_parameters.png",
        "reports/diagnostics/report_velocity_model_physics_bridge.md",
    ),
    StableFigureSpec(
        "diagnostics",
        "fig_velocity_model_physics_bridge.png",
        "reports/diagnostics/report_velocity_model_physics_bridge.md",
    ),
]


def specs_by_category() -> dict[str, list[str]]:
    """返回 stable_export 可直接使用的 category -> filename 清单。"""

    grouped: dict[str, list[str]] = {}
    for spec in STAGE5F_FIGURE_SPECS:
        grouped.setdefault(spec.category, []).append(spec.filename)
    return grouped


def build_figure_metadata(
    *,
    stage: str,
    forward_engine: str,
    velocity_model_type: str,
) -> dict[str, dict[str, Any]]:
    """生成每张精选图的轻量元数据。

    PNG 本身未写入 EXIF/文本块；Stage 5D 采用可审计 manifest 记录图件元数据。
    这样既不破坏 Matplotlib 输出，也能满足“图件必须记录 stage/forward/velocity”
    的审计要求。
    """

    metadata: dict[str, dict[str, Any]] = {}
    for spec in STAGE5F_FIGURE_SPECS:
        metadata[spec.filename] = {
            "stage": stage,
            "forward_engine": forward_engine,
            "velocity_model_type": velocity_model_type,
            "category": spec.category,
            "required_report": spec.required_report,
            "language": "zh",
        }
    return metadata


def expected_category_for_filename(filename: str) -> str | None:
    """查找某张图应该进入的 latest_stable 子目录。"""

    for spec in STAGE5F_FIGURE_SPECS:
        if spec.filename == Path(filename).name:
            return spec.category
    return None


# 兼容旧测试和 Stage 5D/5E 调用名。实际清单已经扩展到 Stage 5F。
STAGE5E_FIGURE_SPECS = STAGE5F_FIGURE_SPECS
STAGE5D_FIGURE_SPECS = STAGE5F_FIGURE_SPECS
