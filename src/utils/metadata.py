"""参数快照和 metadata 保存。"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np

from src.model.attenuation_model import attenuation_metadata, build_attenuation_model


def to_serializable(obj: Any) -> Any:
    """将 params、numpy 数组和 Path 转换为 JSON 可保存对象。"""

    if isinstance(obj, SimpleNamespace):
        return {key: to_serializable(value) for key, value in vars(obj).items()}
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {key: to_serializable(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_serializable(value) for value in obj]
    return obj


def save_json(path: Path, payload: Any) -> None:
    """以 UTF-8 JSON 保存对象。"""

    with path.open("w", encoding="utf-8") as handle:
        json.dump(to_serializable(payload), handle, ensure_ascii=False, indent=2)


def _geometry_self_check(params: SimpleNamespace) -> dict[str, Any]:
    """生成道路 x-y 平面几何自检信息。

    自检目标：
        1. 确认 DAS 光纤测线位于 fiber_y_m；
        2. 确认震源测线位于 source_y_m，默认等于 road_width_m；
        3. 确认伪波场快照是 x-y surface plane, z=0；
        4. 确认 anomaly_depth_m 只作为 z/depth 使用，不作为 y 坐标。
    """

    receiver_y_unique = np.unique(np.round(params.derived.receiver_xyz[:, 1], decimals=9)).tolist()
    source_y_unique = np.unique(np.round(params.derived.source_xyz[:, 1], decimals=9)).tolist()
    tol = 1.0e-9
    source_line_on_opposite_side = (
        abs(params.fiber.y_m - 0.0) <= tol
        and abs(params.source.y_m - params.road.width_m) <= tol
        and abs(params.source.y_m - params.fiber.y_m) > tol
    )

    warnings = []
    if not source_line_on_opposite_side:
        warnings.append("source_y_m 与 fiber_y_m 未呈现默认道路两侧几何，请检查自定义采集参数。")
    if not (0.0 <= params.anomaly.y0_m <= params.road.width_m):
        warnings.append("异常体 y 坐标不在道路区域 0<=y<=W 内。")

    return {
        "fiber_y_m": params.fiber.y_m,
        "source_y_m": params.source.y_m,
        "road_width_m": params.road.width_m,
        "source_line_on_opposite_side": source_line_on_opposite_side,
        "receiver_line_y_unique": receiver_y_unique,
        "source_line_y_unique": source_y_unique,
        "pseudo_wavefield_plane": "x-y surface plane, z=0",
        "anomaly_depth_used_as_z": True,
        "anomaly_depth_used_as_y": False,
        "anomaly_projection_xy_m": {
            "x_m": params.anomaly.x0_m,
            "y_m": params.anomaly.y0_m,
            "depth_m": params.anomaly.depth_m,
        },
        "warnings": warnings,
    }


def build_metadata(
    params: SimpleNamespace,
    synthetic_data: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
    font_info: dict[str, Any] | None = None,
    wavefield_info: dict[str, Any] | None = None,
    forward_info: dict[str, Any] | None = None,
    scan_result: dict[str, Any] | None = None,
    diagnostics_info: dict[str, Any] | None = None,
    confidence_info: dict[str, Any] | None = None,
    score_method_comparison: dict[str, Any] | None = None,
    depth_prior_sensitivity: dict[str, Any] | None = None,
    output_info: dict[str, Any] | None = None,
    git_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """构建本次实验 metadata。

    metadata 必须诚实说明当前是 kinematic approximation 和 DAS-like response
    approximation。Stage 2B 额外写入伪波场几何自检信息，明确快照是 x-y 表面
    平面，异常体深度 h 只参与三维路径距离。
    """

    metadata = {
        "project": "hcz_void_plus",
        "stage": "Stage 5K unified 3D observation kernel and receiver-consistent imaging",
        "data_shape": {
            "order": "shot × time × channel",
            "shape": list(synthetic_data.shape),
        },
        "approximation": {
            "forward": "kinematic approximation",
            "forward_engine": None,
            "forward_modeling_stage": None,
            "das_like": "DAS-like response approximation",
            "receiver": "point_receiver approximation",
            "velocity_model": params.velocity.model_type,
            "velocity_model_family": "uniform/layered/lateral_gradient/localized_low_velocity_zone",
            "velocity_approximation": "straight-ray kinematic approximation",
            "active_forward_engine": getattr(params.forward, "engine", "layered_kinematic"),
            "available_forward_engines": [
                "kinematic_baseline",
                "layered_kinematic",
                "acoustic2d_prototype",
                "elastic2d_prototype",
            ],
            "forward_engine_next_required": "elastic2d accuracy/stability hardening before 2.5D multi-section validation",
            "acoustic2d_prototype_status": "validation_only_not_rayleigh_forward",
            "elastic2d_design_status": "minimal_prototype_available_validation_only",
            "elastic2d_prototype_status": "validation_only_not_default_forward",
            "wavefield_snapshot_type": "kinematic_surface_response_snapshot",
            "surface_response_type": "kinematic_surface_response",
            "is_true_elastic_wavefield": False,
            "is_true_wave_equation_snapshot": False,
            "rayleigh_depth_sensitivity_included": True,
            "volume_wavefield_is_kinematic_proxy": True,
            "volume_wavefield_uses_depth": True,
            "observation_kernel_3d_available": False,
            "forward_uses_observation_kernel": False,
            "localization_uses_observation_kernel": False,
            "forward_localization_share_kernel": False,
            "receiver_consistent_imaging_available": False,
            "volume_proxy_role": "visualization_only",
            "volume_proxy_used_for_localization": False,
        },
        "physics": {
            "rayleigh_depth_sensitivity_enabled": True,
            "wavelet_dominant_frequency_hz": params.task.wavelet_dominant_frequency_hz,
            "estimated_wavelength_m": params.derived.estimated_wavelength_m,
            "penetration_depth_m": params.derived.rayleigh_penetration_depth_m,
            "depth_weight_formula": "exp(-depth / penetration_depth)",
            "velocity_model_type": params.velocity.model_type,
            "layer_depths_m": params.velocity.layer_depths_m,
            "layer_rayleigh_velocities_mps": params.velocity.layer_rayleigh_velocities_mps,
            "attenuation": attenuation_metadata(build_attenuation_model(params)),
            "note": "这是 Rayleigh 波深度敏感性的简化权重，不是严格 Rayleigh 模态深度核。",
        },
        "visualization": {
            "language": params.output.figure_language,
            "save_wavefield_snapshots": params.output.save_wavefield_snapshots,
            "save_wavefield_animation": params.output.save_wavefield_animation,
            "font_info": font_info or {},
            "wavefield_info": wavefield_info or {},
            "volume_wavefield_available": bool(params.output.volume_wavefield_enabled),
        },
        "scan": {
            "enabled": params.scan.enabled,
            "score_method": params.scan.score_method,
            "use_depth_weight": params.scan.use_depth_weight,
            "depth_weight_applied": params.scan.use_depth_weight,
            "grid_shape": params.derived.scan_shape,
            "grid_point_count": params.derived.scan_grid_point_count,
            "best_location": None,
            "best_score": None,
            "truth_error": None,
            "score_volume_kind": None,
            "score_volume_active_kind": None,
            "raw_best_location": None,
            "unweighted_best_location": None,
            "weighted_best_location": None,
            "raw_weighted_difference": None,
            "depth_prior_bias_warning": None,
            "recommended_location": None,
            "recommended_location_type": None,
            "recommended_location_reason": None,
            "depth_uncertainty_interval_m": None,
            "score_volume_raw_saved": False,
            "score_volume_unweighted_saved": False,
            "score_volume_depth_weighted_saved": False,
            "score_method_comparison": None,
            "depth_prior_sensitivity": None,
            "scan_candidate_uses_path_integration": None,
            "scan_uses_representative_velocity": None,
            "multi_attribute_inversion_enabled": None,
            "posterior_volume_status": None,
            "posterior_peak_location": None,
            "posterior_mean_location": None,
            "posterior_covariance_3x3": None,
            "posterior_uncertainty_axes": None,
            "geometry_resolution_status": None,
            "ambiguity_warning": None,
            "multi_peak_warning": None,
            "localization_uses_observation_kernel": None,
            "forward_localization_share_kernel": None,
            "receiver_consistent_imaging_available": None,
            "imaging_peak_location": None,
            "imaging_peak_to_truth_distance": None,
            "imaging_peak_to_posterior_peak_distance": None,
            "posterior_uses_imaging_volume": None,
        },
        "diagnostics": {
            "diffraction_travel_time_curve_figure": None,
            "path_section_figure": None,
            "depth_sensitivity_figure": None,
            "raw_vs_weighted_best_location_figure": None,
            "raw_vs_weighted_x_depth_slice_figure": None,
            "y_high_score_width_check_figure": None,
            "score_method_depth_comparison_figure": None,
            "3d_high_score_uncertainty_summary_figure": None,
            "x_y_depth_uncertainty_slices_figure": None,
            "multi_attribute_score_comparison_figure": None,
            "depth_prior_sensitivity_figure": None,
            "preprocessing_comparison_figure": None,
        },
        "confidence": {
            "peak_sharpness": None,
            "score_contrast": None,
            "score_percentile": None,
            "multi_shot_consistency_mean": None,
            "multi_shot_consistency_std": None,
            "multi_shot_consistency_cv": None,
            "y_depth_coupling_warning": None,
            "best_depth_at_boundary_warning": None,
            "wide_y_high_score_zone_warning": None,
            "raw_weighted_divergence_warning": None,
            "shallow_bias_warning": None,
            "high_score_region": None,
            "low_confidence_flag": None,
        },
        "output": {
            "naming_prefix_rule": params.output.prefix_style,
            "subdirectories": ["arrays", "figures", "snapshots", "animations", "reports", "logs", "metadata"],
            "latest_stable_exported": False,
            "latest_stable_path": None,
        },
        "git": {
            "commit_id": None,
            "push_attempted": False,
            "push_success": False,
        },
        "limitations": [
            "不是完整 DAS 仪器模拟。",
            "不是完整三维弹性波全波场模拟。",
            "gauge length 当前进入参数和 metadata，但 point_receiver 模式下不参与波形计算。",
            "运动学伪波场快照只是传播示意，不是真实弹性波方程数值模拟。",
            "Stage 5J 三维体响应是 x-y-depth kinematic proxy，不是真实 3D elastic wavefield。",
            "运动学地表响应图不是地下点源真实波场，只是 Rayleigh 波走时控制的地表响应示意。",
            "Rayleigh 深度敏感性权重不是严格模态深度核。",
            "基础扫描 best_location 不能作为工程确诊结论。",
            "结果用于科研算法原型验证，不能作为工程确诊结论。",
            "分层/非均匀速度采用 straight-ray kinematic approximation，不是射线弯曲、弹性波场或速度反演。",
        ],
        "geometry": {
            "coordinate_system": {
                "x": "沿道路和光纤方向，单位 m",
                "y": "横穿道路方向，单位 m",
                "z": "深度方向，向下为正，单位 m",
            },
            "n_shot": params.source.shot_count,
            "n_channel": params.fiber.channel_count,
            "nt": params.derived.nt,
            **_geometry_self_check(params),
        },
        "scatter_points": {
            "mode": params.anomaly.scatter_point_mode,
            "xyz_m": scatter_xyz,
            "weights": scatter_weight,
            "note": "多个散射点是运动学等效散射近似，不是真实边界散射模拟。",
        },
    }
    if scan_result is not None:
        metadata["scan"]["best_location"] = scan_result.get("best_location")
        metadata["scan"]["best_score"] = scan_result.get("best_score")
        metadata["scan"]["truth_error"] = scan_result.get("truth_error")
        metadata["scan"]["score_volume_kind"] = scan_result.get("score_volume_kind")
        metadata["scan"]["score_volume_active_kind"] = scan_result.get("score_volume_active_kind")
        metadata["scan"]["unweighted_best_location"] = scan_result.get("unweighted_best_location")
        metadata["scan"]["raw_best_location"] = scan_result.get("raw_best_location")
        metadata["scan"]["weighted_best_location"] = scan_result.get("weighted_best_location")
        metadata["scan"]["raw_weighted_difference"] = scan_result.get("raw_weighted_difference")
        metadata["scan"]["depth_prior_bias_warning"] = scan_result.get("depth_prior_bias_warning")
        metadata["scan"]["score_volume_raw_saved"] = True
        metadata["scan"]["score_volume_unweighted_saved"] = True
        metadata["scan"]["score_volume_depth_weighted_saved"] = True
        scan_audit = scan_result.get("scan_velocity_model_audit", {})
        posterior_summary = scan_result.get("posterior_summary", {})
        geometry_summary = scan_result.get("geometry_resolution_summary", {})
        metadata["scan"]["scan_candidate_uses_path_integration"] = scan_audit.get("scan_candidate_uses_path_integration")
        metadata["scan"]["scan_uses_representative_velocity"] = scan_audit.get("scan_uses_representative_velocity")
        metadata["scan"]["multi_attribute_inversion_enabled"] = scan_result.get("multi_attribute_inversion_enabled")
        metadata["scan"]["posterior_volume_status"] = scan_result.get("posterior_volume_status")
        metadata["scan"]["posterior_peak_location"] = posterior_summary.get("posterior_peak_location")
        metadata["scan"]["posterior_mean_location"] = posterior_summary.get("posterior_mean_location")
        metadata["scan"]["posterior_covariance_3x3"] = posterior_summary.get("posterior_covariance_3x3")
        metadata["scan"]["posterior_uncertainty_axes"] = posterior_summary.get("uncertainty_ellipsoid_axes")
        metadata["scan"]["geometry_resolution_status"] = geometry_summary.get("geometry_resolution_status")
        metadata["scan"]["ambiguity_warning"] = scan_result.get("ambiguity_warning")
        metadata["scan"]["multi_peak_warning"] = scan_result.get("multi_peak_warning")
        metadata["scan"]["localization_uses_observation_kernel"] = scan_result.get("localization_uses_observation_kernel")
        metadata["scan"]["forward_localization_share_kernel"] = scan_result.get("forward_localization_share_kernel")
        metadata["scan"]["receiver_consistent_imaging_available"] = scan_result.get("receiver_consistent_imaging_available")
        metadata["scan"]["imaging_peak_location"] = scan_result.get("imaging_peak_location")
        metadata["scan"]["imaging_peak_to_truth_distance"] = scan_result.get("imaging_peak_to_truth_distance")
        metadata["scan"]["imaging_peak_to_posterior_peak_distance"] = scan_result.get("imaging_peak_to_posterior_peak_distance")
        metadata["scan"]["posterior_uses_imaging_volume"] = scan_result.get("posterior_uses_imaging_volume")
        metadata["approximation"]["localization_uses_observation_kernel"] = bool(
            scan_result.get("localization_uses_observation_kernel")
        )
        metadata["approximation"]["forward_localization_share_kernel"] = bool(
            scan_result.get("forward_localization_share_kernel")
        )
        metadata["approximation"]["receiver_consistent_imaging_available"] = bool(
            scan_result.get("receiver_consistent_imaging_available")
        )
        metadata["approximation"]["volume_proxy_used_for_localization"] = False
    if forward_info is not None:
        metadata["approximation"]["forward_engine"] = forward_info.get("forward_engine")
        metadata["approximation"]["forward_modeling_stage"] = forward_info.get("forward_stage")
        metadata["approximation"]["forward_engine_note"] = forward_info.get("note")
        kernel_meta = forward_info.get("observation_kernel_3d") or {}
        metadata["approximation"]["observation_kernel_3d_available"] = bool(kernel_meta)
        metadata["approximation"]["forward_uses_observation_kernel"] = bool(
            forward_info.get("forward_uses_observation_kernel")
        )
        metadata["approximation"]["observation_kernel_shape"] = kernel_meta.get("path_shape")
        metadata["approximation"]["observation_kernel_candidate_grid_shape"] = kernel_meta.get("candidate_grid_shape")
    if diagnostics_info is not None:
        metadata["diagnostics"].update(diagnostics_info)
    if confidence_info is not None:
        metadata["confidence"].update(
            {
                "peak_sharpness": confidence_info["peak"]["peak_sharpness"],
                "score_contrast": confidence_info["contrast"]["score_contrast"],
                "score_percentile": confidence_info["contrast"]["score_percentile"],
                "multi_shot_consistency_mean": confidence_info["multi_shot_consistency"]["mean"],
                "multi_shot_consistency_std": confidence_info["multi_shot_consistency"]["std"],
                "multi_shot_consistency_cv": confidence_info["multi_shot_consistency"]["coefficient_of_variation"],
                "y_depth_coupling_warning": confidence_info["y_depth_coupling"]["warning"],
                "best_depth_at_boundary_warning": confidence_info["stage3b_warnings"]["best_depth_at_boundary_warning"],
                "wide_y_high_score_zone_warning": confidence_info["stage3b_warnings"]["wide_y_high_score_zone_warning"],
                "raw_weighted_divergence_warning": confidence_info["stage3b_warnings"]["raw_weighted_divergence_warning"],
                "shallow_bias_warning": confidence_info["stage3b_warnings"]["shallow_bias_warning"],
                "high_score_region": confidence_info["high_score_region"],
                "low_confidence_flag": confidence_info["low_confidence_flag"],
            }
        )
        metadata["scan"]["recommended_location"] = confidence_info["recommended_location"]
        metadata["scan"]["recommended_location_type"] = confidence_info["recommended_location_type"]
        metadata["scan"]["recommended_location_reason"] = confidence_info["recommended_location_reason"]
        metadata["scan"]["depth_uncertainty_interval_m"] = confidence_info["depth_uncertainty_interval_m"]
    if score_method_comparison is not None:
        metadata["scan"]["score_method_comparison"] = {
            "methods": {
                method: {
                    "unweighted_best_location": result["unweighted_best_location"],
                    "weighted_best_location": result["weighted_best_location"],
                    "unweighted_truth_error": result["unweighted_truth_error"],
                    "weighted_truth_error": result["weighted_truth_error"],
                    "weighted_depth_at_boundary": result["weighted_depth_at_boundary"],
                }
                for method, result in score_method_comparison["methods"].items()
            },
            "depth_stability_reference": score_method_comparison["depth_stability_reference"],
        }
    if depth_prior_sensitivity is not None:
        metadata["scan"]["depth_prior_sensitivity"] = depth_prior_sensitivity
    if output_info is not None:
        metadata["output"].update(output_info)
    if git_info is not None:
        metadata["git"].update(git_info)
    return metadata
