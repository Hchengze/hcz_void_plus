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
        "F3": "elastic2d：下一步 Rayleigh/free-surface/void scattering 核心方向。",
        "F4": "2.5D / multi-section elastic validation。",
        "F5": "local small-domain 3D elastic validation。",
        "F6": "external solver adapters，不复制第三方代码。",
    }

    return {
        "stage": "Stage 5B",
        "stable_area": "code/current_3d_algorithm",
        "research_area": "src",
        "geometry": "3D source_xyz / receiver_xyz / candidate_xyz",
        "forward": "layered_kinematic straight-ray kinematic approximation",
        "stable_forward_engine": "layered_kinematic",
        "available_validation_forward": "acoustic2d_prototype",
        "planned_physics_forward": "elastic2d",
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
        "main_localization": "multi_attribute_unweighted",
        "depth_weighting": "diagnostic only by default",
        "result_expression": "3D high-score region + uncertainty interval",
        "not_engineering_diagnosis": True,
    }
