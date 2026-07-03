"""参数快照和 metadata 保存。"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np


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
    scan_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """构建本次实验 metadata。

    metadata 必须诚实说明当前是 kinematic approximation 和 DAS-like response
    approximation。Stage 2B 额外写入伪波场几何自检信息，明确快照是 x-y 表面
    平面，异常体深度 h 只参与三维路径距离。
    """

    metadata = {
        "project": "hcz_void_plus",
        "stage": "Stage 2B pseudo-wavefield geometry layout self-check",
        "data_shape": {
            "order": "shot × time × channel",
            "shape": list(synthetic_data.shape),
        },
        "approximation": {
            "forward": "kinematic approximation",
            "das_like": "DAS-like response approximation",
            "receiver": "point_receiver approximation",
            "velocity_model": "uniform effective Rayleigh velocity",
            "wavefield_snapshot_type": "kinematic_pseudo_wavefield",
            "is_true_elastic_wavefield": False,
        },
        "visualization": {
            "language": params.output.figure_language,
            "save_wavefield_snapshots": params.output.save_wavefield_snapshots,
            "save_wavefield_animation": params.output.save_wavefield_animation,
            "font_info": font_info or {},
            "wavefield_info": wavefield_info or {},
        },
        "scan": {
            "enabled": params.scan.enabled,
            "score_method": params.scan.score_method,
            "grid_shape": params.derived.scan_shape,
            "grid_point_count": params.derived.scan_grid_point_count,
            "best_location": None,
            "best_score": None,
            "truth_error": None,
        },
        "output": {
            "naming_prefix_rule": params.output.prefix_style,
            "subdirectories": ["arrays", "figures", "snapshots", "animations", "reports", "logs", "metadata"],
        },
        "limitations": [
            "不是完整 DAS 仪器模拟。",
            "不是完整三维弹性波全波场模拟。",
            "gauge length 当前进入参数和 metadata，但 point_receiver 模式下不参与波形计算。",
            "运动学伪波场快照只是传播示意，不是真实弹性波方程数值模拟。",
            "基础扫描 best_location 不能作为工程确诊结论。",
            "结果用于科研算法原型验证，不能作为工程确诊结论。",
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
    return metadata
