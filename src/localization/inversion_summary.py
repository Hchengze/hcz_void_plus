"""三维反演诊断摘要。

该模块只组织 metadata/report 中需要的关键字段，避免 full_pipeline 到处拼接字典。
"""

from __future__ import annotations

from typing import Any


def build_inversion_summary(scan_result: dict[str, Any]) -> dict[str, Any]:
    """从 scan_result 提取 Stage 5I 三维反演主线字段。"""

    posterior = scan_result.get("posterior_summary", {})
    uncertainty = scan_result.get("uncertainty_summary", {})
    geometry = scan_result.get("geometry_resolution_summary", {})
    audit = scan_result.get("scan_velocity_model_audit", {})
    return {
        "scan_candidate_uses_path_integration": audit.get("scan_candidate_uses_path_integration"),
        "scan_uses_representative_velocity": audit.get("scan_uses_representative_velocity"),
        "multi_attribute_inversion_enabled": scan_result.get("multi_attribute_inversion_enabled"),
        "posterior_volume_status": scan_result.get("posterior_volume_status"),
        "posterior_peak_location": posterior.get("posterior_peak_location"),
        "posterior_mean_location": posterior.get("posterior_mean_location"),
        "posterior_uncertainty_axes": posterior.get("uncertainty_ellipsoid_axes"),
        "posterior_covariance_3x3": posterior.get("posterior_covariance_3x3"),
        "geometry_resolution_status": geometry.get("geometry_resolution_status"),
        "ambiguity_warning": uncertainty.get("ambiguity_warning"),
        "y_depth_coupling_warning": uncertainty.get("y_depth_coupling_warning"),
        "multi_peak_warning": uncertainty.get("multi_peak_warning"),
        "ready_for_2p5d": False,
    }
