"""Stage 5G latest_stable 精选清单。

本模块只定义哪些当前结果允许进入 ``outputs/latest_stable``。Stage 5G
把 Stage 5F 的 core/diagnostics/uncertainty 细分类收敛为三类：
forward、localization、error_analysis。这样人工复查时先看三条主线，而不是在
历史图件里找结论。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StableFigureSpec:
    """latest_stable 静态图条目。"""

    category: str
    filename: str
    required_report: str


@dataclass(frozen=True)
class StableAnimationSpec:
    """latest_stable 动图条目。"""

    category: str
    filename: str
    required_report: str


STAGE5G_FIGURE_SPECS: list[StableFigureSpec] = [
    StableFigureSpec("forward", "fig_geometry_3d_overview.png", "reports/forward/report_full_pipeline.md"),
    StableFigureSpec("forward", "fig_velocity_model_active_badge.png", "reports/forward/report_velocity_model_audit.md"),
    StableFigureSpec("forward", "fig_velocity_model_physics_bridge.png", "reports/forward/report_velocity_model_physics_bridge.md"),
    StableFigureSpec("forward", "fig_velocity_sampling_paths_3d.png", "reports/forward/report_velocity_model_visualization.md"),
    StableFigureSpec("forward", "fig_elastic2d_rayleigh_benchmark_matrix.png", "reports/forward/report_elastic2d_rayleigh_benchmark.md"),
    StableFigureSpec("forward", "fig_elastic2d_rayleigh_velocity_error.png", "reports/forward/report_elastic2d_rayleigh_benchmark.md"),
    StableFigureSpec("forward", "fig_elastic2d_surface_event_ridge.png", "reports/forward/report_elastic2d_rayleigh_benchmark.md"),
    StableFigureSpec("forward", "fig_elastic2d_das_best_case.png", "reports/forward/report_elastic2d_das_response.md"),
    StableFigureSpec("forward", "fig_single_shot_wavefield_snapshots.png", "reports/forward/report_full_pipeline.md"),
    StableFigureSpec("forward", "fig_elastic2d_boundary_reflection_diagnostics.png", "reports/forward/report_elastic2d_boundary_validation.md"),
    StableFigureSpec("localization", "fig_scan_x_y_slice.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("localization", "fig_scan_x_depth_slice.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("localization", "fig_3d_high_score_region.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("localization", "fig_recommended_location_3d.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("localization", "fig_3d_uncertainty_box.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("localization", "fig_x_y_depth_uncertainty_slices.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("error_analysis", "fig_stage5g_status_badge.png", "reports/error_analysis/report_latest_stable_file_audit.md"),
    StableFigureSpec("error_analysis", "fig_latest_stable_quality_summary.png", "reports/error_analysis/report_figure_quality_check.md"),
    StableFigureSpec("error_analysis", "fig_rayleigh_pick_interpretation.png", "reports/forward/report_elastic2d_rayleigh_benchmark.md"),
    StableFigureSpec("error_analysis", "fig_elastic2d_das_report_consistency.png", "reports/forward/report_elastic2d_das_response.md"),
    StableFigureSpec("error_analysis", "fig_elastic_vs_kinematic_energy_partition.png", "reports/error_analysis/report_elastic_vs_kinematic.md"),
    StableFigureSpec("error_analysis", "fig_confidence_diagnostics.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("error_analysis", "fig_model_mismatch_error_summary.png", "reports/error_analysis/report_model_mismatch.md"),
]


STAGE5G_ANIMATION_SPECS: list[StableAnimationSpec] = [
    StableAnimationSpec("forward", "anim_multishot_forward_overview.gif", "reports/forward/report_full_pipeline.md"),
    StableAnimationSpec("forward", "anim_single_shot_wavefield.gif", "reports/forward/report_full_pipeline.md"),
]


def specs_by_category() -> dict[str, list[str]]:
    """返回静态图 category -> filename 清单。"""

    grouped: dict[str, list[str]] = {}
    for spec in STAGE5G_FIGURE_SPECS:
        grouped.setdefault(spec.category, []).append(spec.filename)
    return grouped


def animation_specs_by_category() -> dict[str, list[str]]:
    """返回动图 category -> filename 清单。"""

    grouped: dict[str, list[str]] = {}
    for spec in STAGE5G_ANIMATION_SPECS:
        grouped.setdefault(spec.category, []).append(spec.filename)
    return grouped


def build_figure_metadata(
    *,
    stage: str,
    forward_engine: str,
    velocity_model_type: str,
) -> dict[str, dict[str, Any]]:
    """生成每张精选图的审计 metadata。"""

    metadata: dict[str, dict[str, Any]] = {}
    for spec in STAGE5G_FIGURE_SPECS:
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
    """查找图件应该进入的 Stage 5G latest_stable 子目录。"""

    for spec in STAGE5G_FIGURE_SPECS:
        if spec.filename == Path(filename).name:
            return spec.category
    return None


# 兼容旧测试或旧导入名。实际清单以 Stage 5G 为准。
STAGE5F_FIGURE_SPECS = STAGE5G_FIGURE_SPECS
STAGE5E_FIGURE_SPECS = STAGE5G_FIGURE_SPECS
STAGE5D_FIGURE_SPECS = STAGE5G_FIGURE_SPECS
