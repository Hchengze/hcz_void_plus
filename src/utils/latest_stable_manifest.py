"""Stage 5J latest_stable 精选清单。

本模块只定义哪些当前结果允许进入 ``outputs/latest_stable``。Stage 5G
把 Stage 5F 的 core/diagnostics/uncertainty 细分类收敛为三类：
forward、localization、error_analysis。这样人工复查时先看三条主线，而不是在
历史图件里找结论。Stage 5J 保持三类结构，但 forward 主图改为三维运动学体响应、
速度模型上下文炮集和 attenuation 对照。
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


STAGE5K_FIGURE_SPECS: list[StableFigureSpec] = [
    StableFigureSpec("forward", "fig_geometry_3d_overview.png", "reports/forward/report_full_pipeline.md"),
    StableFigureSpec("forward", "fig_velocity_model_active_badge.png", "reports/forward/report_velocity_model_audit.md"),
    StableFigureSpec("forward", "fig_velocity_sampling_paths_3d.png", "reports/forward/report_velocity_model_visualization.md"),
    StableFigureSpec("forward", "fig_volume_wavefield_xyz_slices.png", "reports/forward/report_full_pipeline.md"),
    StableFigureSpec("forward", "fig_volume_wavefield_depth_slices.png", "reports/forward/report_full_pipeline.md"),
    StableFigureSpec("forward", "fig_volume_wavefield_3d_energy_proxy.png", "reports/forward/report_full_pipeline.md"),
    StableFigureSpec("forward", "fig_shot_gather_with_velocity_model.png", "reports/forward/report_full_pipeline.md"),
    StableFigureSpec("forward", "fig_shot_gather_attenuation_comparison.png", "reports/forward/report_full_pipeline.md"),
    StableFigureSpec("forward", "fig_elastic2d_rayleigh_benchmark_matrix.png", "reports/forward/report_elastic2d_rayleigh_benchmark.md"),
    StableFigureSpec("forward", "fig_elastic2d_das_best_case.png", "reports/forward/report_elastic2d_das_response.md"),
    StableFigureSpec("localization", "fig_scan_x_y_slice.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("localization", "fig_3d_high_score_region.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("localization", "fig_recommended_location_3d.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("localization", "fig_3d_uncertainty_box.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("localization", "fig_receiver_consistent_imaging_volume.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("localization", "fig_kernel_shared_posterior_volume.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("localization", "fig_3d_uncertainty_ellipsoid.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("error_analysis", "fig_stage5j_status_badge.png", "reports/error_analysis/report_manual_review_readiness.md"),
    StableFigureSpec("error_analysis", "fig_rayleigh_pick_interpretation.png", "reports/forward/report_elastic2d_rayleigh_benchmark.md"),
    StableFigureSpec("error_analysis", "fig_elastic2d_das_report_consistency.png", "reports/forward/report_elastic2d_das_response.md"),
    StableFigureSpec("error_analysis", "fig_module_coordination_summary.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("error_analysis", "fig_3d_geometry_resolution_analysis.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("error_analysis", "fig_scan_velocity_model_consistency.png", "reports/localization/report_full_pipeline.md"),
    StableFigureSpec("error_analysis", "fig_receiver_imaging_vs_volume_proxy.png", "reports/localization/report_full_pipeline.md"),
]


STAGE5K_ANIMATION_SPECS: list[StableAnimationSpec] = [
    StableAnimationSpec("forward", "anim_multishot_forward_overview.gif", "reports/forward/report_full_pipeline.md"),
    StableAnimationSpec("forward", "anim_single_shot_volume_wavefield.gif", "reports/forward/report_full_pipeline.md"),
]


def specs_by_category() -> dict[str, list[str]]:
    """返回静态图 category -> filename 清单。"""

    grouped: dict[str, list[str]] = {}
    for spec in STAGE5K_FIGURE_SPECS:
        grouped.setdefault(spec.category, []).append(spec.filename)
    return grouped


def animation_specs_by_category() -> dict[str, list[str]]:
    """返回动图 category -> filename 清单。"""

    grouped: dict[str, list[str]] = {}
    for spec in STAGE5K_ANIMATION_SPECS:
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
    for spec in STAGE5K_FIGURE_SPECS:
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
    """查找图件应该进入的 Stage 5J latest_stable 子目录。"""

    for spec in STAGE5K_FIGURE_SPECS:
        if spec.filename == Path(filename).name:
            return spec.category
    return None


STAGE5J_FIGURE_SPECS = STAGE5K_FIGURE_SPECS
STAGE5J_ANIMATION_SPECS = STAGE5K_ANIMATION_SPECS


# 兼容旧测试或旧导入名。实际清单以 Stage 5J 为准。
STAGE5H_FIGURE_SPECS = STAGE5J_FIGURE_SPECS
STAGE5H_ANIMATION_SPECS = STAGE5J_ANIMATION_SPECS
STAGE5G_FIGURE_SPECS = STAGE5J_FIGURE_SPECS
STAGE5G_ANIMATION_SPECS = STAGE5J_ANIMATION_SPECS
STAGE5F_FIGURE_SPECS = STAGE5J_FIGURE_SPECS
STAGE5E_FIGURE_SPECS = STAGE5J_FIGURE_SPECS
STAGE5D_FIGURE_SPECS = STAGE5J_FIGURE_SPECS
STAGE5H_FIGURE_SPECS = STAGE5K_FIGURE_SPECS
STAGE5H_ANIMATION_SPECS = STAGE5K_ANIMATION_SPECS
STAGE5G_FIGURE_SPECS = STAGE5K_FIGURE_SPECS
STAGE5G_ANIMATION_SPECS = STAGE5K_ANIMATION_SPECS
STAGE5F_FIGURE_SPECS = STAGE5K_FIGURE_SPECS
STAGE5E_FIGURE_SPECS = STAGE5K_FIGURE_SPECS
STAGE5D_FIGURE_SPECS = STAGE5K_FIGURE_SPECS
