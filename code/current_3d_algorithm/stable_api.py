"""当前稳定三维算法区的轻量 API。

该 API 不重新实现算法，只给出当前推荐主线并调用 src/ 中经过测试的研发实现。
这样可以避免 code/ 与 src/ 复制分叉，同时满足用户对“最新稳定成果区”的要求。
"""

from __future__ import annotations

from typing import Any


def get_current_algorithm_summary() -> dict[str, Any]:
    """返回当前稳定算法说明。

    输出内容用于测试、文档和人工审计。这里明确写出：当前不是工程确诊系统，
    速度模型也只是 straight-ray kinematic approximation。
    """

    forward_roadmap = {
        "F0": "kinematic_baseline：快速均匀速度运动学基线，不是当前主正演。",
        "F1": "layered_kinematic：当前主定位 forward，straight-ray kinematic approximation。",
        "F2": "acoustic2d_prototype：声学波动方程基础设施验证，不代表 Rayleigh 波。",
        "F3": "elastic2d_prototype：Rayleigh/free-surface/void scattering 局部物理验证起点，Stage 5I 仍只作为 validation，不替代三维运动学定位主线。",
        "F4": "2.5D / multi-section elastic validation。",
        "F5": "local small-domain 3D elastic validation。",
        "F6": "external solver adapters，不复制第三方代码。",
    }

    return {
        "stage": "Stage 5I",
        "stable_area": "code/current_3d_algorithm",
        "research_area": "src",
        "geometry": "3D source_xyz / receiver_xyz / candidate_xyz",
        "forward": "layered_kinematic straight-ray kinematic approximation",
        "stable_forward_engine": "layered_kinematic",
        "available_validation_forward": [
            "acoustic2d_prototype",
            "elastic2d_prototype",
            "staggered_elastic2d_benchmark",
        ],
        "planned_physics_forward": "elastic2d accuracy/stability hardening before 2.5D multi-section validation",
        "velocity_model_audit": "direct/scatter/scan travel-time must use the velocity_model interface",
        "latest_stable_policy": "three-category curated outputs only after figure self-check",
        "scientific_latest_stable_policy": "reports and figures must not claim Rayleigh/DAS success when diagnostics fail",
        "stage5d_diagnostics": [
            "repository_health_report",
            "figure_self_check_report",
            "velocity_model_audit_report",
            "velocity_model_visualization",
            "elastic2d_rayleigh_pick_diagnostics",
            "elastic2d_void_parameter_sensitivity",
            "elastic2d_das_component_response",
            "elastic_vs_kinematic_energy_partition",
        ],
        "stage5e_diagnostics": [
            "scientific_figure_self_check",
            "elastic2d_numerical_sensitivity",
            "velocity_model_physics_bridge",
            "das_gauge_nonzero_check",
            "staggered_grid_layout_plan",
        ],
        "stage5f_diagnostics": [
            "document_cleanup_report",
            "figure_quality_check",
            "figure_deduplication",
            "figure_language_check",
            "latest_stable_curator",
            "elastic2d_rayleigh_benchmark",
            "three_dimensional_forward_validation_policy",
        ],
        "stage5g_diagnostics": [
            "latest_stable_three_category_structure",
            "figure_label_audit",
            "forward_and_localization_animations",
            "geometry_3d_overview",
            "velocity_sampling_paths_3d",
            "3d_high_score_region",
            "3d_uncertainty_box",
            "testing_strategy",
        ],
        "stage5h_diagnostics": [
            "algorithm_commit_and_latest_stable_commit_metadata",
            "latest_stable_tree_snapshot",
            "manual_review_readiness",
            "3d_figure_readability_notes",
            "rayleigh_picked_event_interpretation",
            "das_gauge_weak_response_explanation",
        ],
        "stage5i_diagnostics": [
            "scan_velocity_model_path_integration_audit",
            "multi_attribute_3d_score_volumes",
            "posterior_probability_volume",
            "uncertainty_ellipsoid_axes",
            "geometry_resolution_volume",
            "3d_connected_components",
        ],
        "rayleigh_like_stage5d_status": "not_detected",
        "das_gauge_stage5d_status": "zero_or_too_weak",
        "rayleigh_benchmark_stage5f_status": "not_passed",
        "das_gauge_default_localization": False,
        "ready_for_2p5d": False,
        "forward_roadmap": forward_roadmap,
        "velocity_default": "layered",
        "velocity_models": [
            "uniform",
            "layered",
            "lateral_gradient",
            "localized_low_velocity_zone",
            "layered_with_anomaly_perturbation",
        ],
        "recommended_preprocessing": "bandpass + trace_normalization + taper direct mute",
        "main_localization": "multi_attribute_3d_posterior_like",
        "depth_weighting": "diagnostic only by default",
        "result_expression": "3D high-score region + uncertainty interval",
        "not_engineering_diagnosis": True,
    }
