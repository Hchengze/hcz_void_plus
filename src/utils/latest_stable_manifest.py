"""latest_stable 精选清单与图件元数据。

本模块只描述“哪些当前阶段成果允许进入 latest_stable”，不负责生成图件本身。
这样做的目的，是把 Stage 5D 的图件自检从简单文件复制升级为可审计流程：
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


STAGE5D_FIGURE_SPECS: list[StableFigureSpec] = [
    StableFigureSpec("core", "fig_geometry_layout_check.png", "reports/core/report_full_pipeline.md"),
    StableFigureSpec("core", "fig_shot_gather_000.png", "reports/core/report_full_pipeline.md"),
    StableFigureSpec("core", "fig_best_location_map.png", "reports/core/report_full_pipeline.md"),
    StableFigureSpec("core", "fig_confidence_diagnostics.png", "reports/core/report_confidence.md"),
    StableFigureSpec("core", "fig_forward_roadmap_status.png", "reports/forward/report_forward_engine_ablation.md"),
    StableFigureSpec("forward", "fig_forward_engine_comparison.png", "reports/forward/report_forward_engine_ablation.md"),
    StableFigureSpec(
        "forward",
        "fig_layered_kinematic_vs_baseline_gather.png",
        "reports/forward/report_forward_engine_ablation.md",
    ),
    StableFigureSpec("forward", "fig_acoustic2d_wavefield_snapshots.png", "reports/forward/report_acoustic2d_prototype.md"),
    StableFigureSpec("forward", "fig_acoustic2d_shot_gather.png", "reports/forward/report_acoustic2d_prototype.md"),
    StableFigureSpec(
        "forward",
        "fig_elastic2d_rayleigh_wavefield_snapshots.png",
        "reports/forward/report_elastic2d_rayleigh_validation.md",
    ),
    StableFigureSpec("forward", "fig_elastic2d_surface_gather.png", "reports/forward/report_elastic2d_rayleigh_validation.md"),
    StableFigureSpec(
        "forward",
        "fig_elastic2d_rayleigh_velocity_check.png",
        "reports/forward/report_elastic2d_rayleigh_validation.md",
    ),
    StableFigureSpec(
        "forward",
        "fig_elastic2d_rayleigh_pick_diagnostics.png",
        "reports/forward/report_elastic2d_rayleigh_validation.md",
    ),
    StableFigureSpec(
        "forward",
        "fig_elastic2d_void_scattering_residual.png",
        "reports/forward/report_elastic2d_void_scattering.md",
    ),
    StableFigureSpec(
        "forward",
        "fig_elastic2d_void_diffraction_overlay.png",
        "reports/forward/report_elastic2d_void_scattering.md",
    ),
    StableFigureSpec(
        "forward",
        "fig_elastic2d_void_parameter_sensitivity.png",
        "reports/forward/report_elastic2d_void_scattering.md",
    ),
    StableFigureSpec(
        "forward",
        "fig_elastic2d_void_residual_energy_map.png",
        "reports/forward/report_elastic2d_void_scattering.md",
    ),
    StableFigureSpec("forward", "fig_elastic2d_das_gauge_response.png", "reports/forward/report_elastic2d_das_response.md"),
    StableFigureSpec(
        "forward",
        "fig_elastic2d_das_component_comparison.png",
        "reports/forward/report_elastic2d_das_response.md",
    ),
    StableFigureSpec(
        "forward",
        "fig_elastic2d_das_gauge_length_sensitivity.png",
        "reports/forward/report_elastic2d_das_response.md",
    ),
    StableFigureSpec("forward", "fig_elastic_vs_kinematic_overlay.png", "reports/forward/report_elastic_vs_kinematic.md"),
    StableFigureSpec(
        "forward",
        "fig_elastic_vs_kinematic_residual_energy.png",
        "reports/forward/report_elastic_vs_kinematic.md",
    ),
    StableFigureSpec(
        "forward",
        "fig_elastic_vs_kinematic_energy_partition.png",
        "reports/forward/report_elastic_vs_kinematic.md",
    ),
    StableFigureSpec("localization", "fig_scan_x_depth_slice.png", "reports/core/report_full_pipeline.md"),
    StableFigureSpec("localization", "fig_scan_x_y_slice.png", "reports/core/report_full_pipeline.md"),
    StableFigureSpec("localization", "fig_multi_attribute_ablation.png", "reports/localization/report_multi_attribute_ablation.md"),
    StableFigureSpec("uncertainty", "fig_3d_high_score_components.png", "reports/core/report_confidence.md"),
    StableFigureSpec("uncertainty", "fig_x_y_depth_uncertainty_slices.png", "reports/core/report_confidence.md"),
    StableFigureSpec("uncertainty", "fig_recommendation_decision_flow.png", "reports/core/report_confidence.md"),
    StableFigureSpec("diagnostics", "fig_velocity_model_comparison.png", "reports/diagnostics/report_velocity_model_ablation.md"),
    StableFigureSpec("diagnostics", "fig_model_mismatch_error_summary.png", "reports/diagnostics/report_model_mismatch.md"),
    StableFigureSpec("diagnostics", "fig_depth_prior_sensitivity.png", "reports/core/report_confidence.md"),
    StableFigureSpec(
        "diagnostics",
        "fig_velocity_model_profile_current.png",
        "reports/diagnostics/report_velocity_model_visualization.md",
    ),
    StableFigureSpec(
        "diagnostics",
        "fig_velocity_model_2d_slice_current.png",
        "reports/diagnostics/report_velocity_model_visualization.md",
    ),
    StableFigureSpec(
        "diagnostics",
        "fig_velocity_sampling_paths_current.png",
        "reports/diagnostics/report_velocity_model_visualization.md",
    ),
    StableFigureSpec(
        "diagnostics",
        "fig_uniform_vs_layered_travel_time_difference.png",
        "reports/diagnostics/report_velocity_model_visualization.md",
    ),
    StableFigureSpec(
        "diagnostics",
        "fig_velocity_model_active_badge.png",
        "reports/diagnostics/report_velocity_model_audit.md",
    ),
]


def specs_by_category() -> dict[str, list[str]]:
    """返回 stable_export 可直接使用的 category -> filename 清单。"""

    grouped: dict[str, list[str]] = {}
    for spec in STAGE5D_FIGURE_SPECS:
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
    for spec in STAGE5D_FIGURE_SPECS:
        metadata[spec.filename] = {
            "stage": stage,
            "forward_engine": forward_engine,
            "velocity_model_type": velocity_model_type,
            "category": spec.category,
            "required_report": spec.required_report,
        }
    return metadata


def expected_category_for_filename(filename: str) -> str | None:
    """查找某张图应该进入的 latest_stable 子目录。"""

    for spec in STAGE5D_FIGURE_SPECS:
        if spec.filename == Path(filename).name:
            return spec.category
    return None
