"""参数快照和 metadata 保存。"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np


def to_serializable(obj: Any) -> Any:
    """将 params、numpy 数组和 Path 转换为 JSON 可保存对象。

    物理意义：
        科研结果必须可追溯。params_snapshot.json 需要包含默认参数、命令行覆盖
        参数和派生参数，因此要把 numpy 数组等对象转换为普通列表。
    """

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

    metadata 必须诚实说明：
        当前是 kinematic approximation；
        当前是 DAS-like response approximation；
        当前速度模型为 uniform effective Rayleigh velocity；
        当前结果不能作为工程确诊结论。
    """

    metadata = {
        "project": "hcz_void_plus",
        "stage": "Stage 2 Chinese visualization and basic scan localization",
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
