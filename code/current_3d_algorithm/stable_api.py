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

    return {
        "stage": "Stage 5A",
        "stable_area": "code/current_3d_algorithm",
        "research_area": "src",
        "geometry": "3D source_xyz / receiver_xyz / candidate_xyz",
        "forward": "DAS-like response approximation + kinematic approximation",
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
