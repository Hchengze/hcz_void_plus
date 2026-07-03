"""Stage 2 基础多炮扫描定位 pipeline。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np

from src.features.direct_arrival import predict_direct_arrival_times
from src.features.direct_wave_mute import mute_direct_wave
from src.localization.multishot_scan import run_multishot_scan
from src.localization.scan_grid import build_scan_grid
from src.model.velocity_model import build_velocity_model
from src.utils.metadata import build_metadata, save_json
from src.utils.path_manager import ensure_output_subdirs
from src.visualization.plot_scan import plot_best_location_map, plot_scan_x_depth_slice, plot_scan_x_y_slice


def _write_scan_report(params: SimpleNamespace, output_path: Path, scan_result: dict[str, Any]) -> None:
    """写出中文扫描定位报告。"""

    best = scan_result["best_location"]
    error = scan_result["truth_error"]
    content = f"""# 扫描定位报告

## 当前近似

- 扫描方法：`{params.scan.score_method}`
- 物理基础：运动学等效散射走时 + 局部能量聚焦
- 这不是 FWI，不是完整成像，也不是工程确诊。

## 扫描网格

- x：`{params.scan.x_min_m}` 到 `{params.scan.x_max_m}` m，步长 `{params.scan.x_step_m}` m
- y：`{params.scan.y_min_m}` 到 `{params.scan.y_max_m}` m，步长 `{params.scan.y_step_m}` m
- h：`{params.scan.depth_min_m}` 到 `{params.scan.depth_max_m}` m，步长 `{params.scan.depth_step_m}` m
- score_volume shape：`{tuple(scan_result["score_volume"].shape)}`

## 结果

- best_location：x=`{best["x_m"]}` m，y=`{best["y_m"]}` m，h=`{best["depth_m"]}` m
- best_score：`{scan_result["best_score"]}`
- truth_error：dx=`{error["dx_m"]}` m，dy=`{error["dy_m"]}` m，dh=`{error["ddepth_m"]}` m，三维距离=`{error["distance_m"]}` m

## 风险提示

{scan_result["y_depth_coupling_warning"]}
"""
    output_path.write_text(content, encoding="utf-8")


def run_scan_pipeline(params: SimpleNamespace, forward_result: dict[str, Any] | None = None) -> dict[str, Any]:
    """运行基础 x-y-h 多炮扫描定位。

    如果 forward_result 已提供，则复用正演数据；否则尝试按当前 params 的输出目录
    读取数组。本项目主路径由 full_pipeline 提供 forward_result。
    """

    paths = forward_result["paths"] if forward_result is not None else ensure_output_subdirs(params)
    if forward_result is None:
        synthetic_data = np.load(paths["arrays"] / "arr_synthetic_data.npy")
        source_xyz = params.derived.source_xyz
        receiver_xyz = params.derived.receiver_xyz
        velocity_model = build_velocity_model(params)
        scatter_xyz = np.array([[params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m]], dtype=float)
        scatter_weight = np.array([params.anomaly.scatter_strength], dtype=float)
        font_info = {}
        wavefield_info = {}
    else:
        synthetic_data = forward_result["synthetic_data"]
        source_xyz = forward_result["source_xyz"]
        receiver_xyz = forward_result["receiver_xyz"]
        velocity_model = forward_result["velocity_model"]
        scatter_xyz = forward_result["scatter_xyz"]
        scatter_weight = forward_result["scatter_weight"]
        font_info = forward_result.get("font_info", {})
        wavefield_info = forward_result.get("wavefield_info", {})

    direct_times = predict_direct_arrival_times(params, source_xyz, receiver_xyz, velocity_model)
    scan_data = synthetic_data
    if params.scan.direct_mute_enabled:
        scan_data = mute_direct_wave(scan_data, params.derived.time_axis, direct_times, params.scan.direct_mute_half_width_s)

    scan_grid = build_scan_grid(params)
    scan_result = run_multishot_scan(
        scan_data,
        params.derived.time_axis,
        source_xyz,
        receiver_xyz,
        velocity_model,
        scan_grid,
        params,
    )

    if params.output.save_arrays:
        np.save(paths["arrays"] / "arr_score_volume.npy", scan_result["score_volume"])
        np.save(paths["arrays"] / "arr_scan_x_grid.npy", params.derived.scan_x_grid)
        np.save(paths["arrays"] / "arr_scan_y_grid.npy", params.derived.scan_y_grid)
        np.save(paths["arrays"] / "arr_scan_depth_grid.npy", params.derived.scan_depth_grid)
        np.save(paths["arrays"] / "arr_direct_times.npy", direct_times)

    if params.output.save_figures:
        plot_scan_x_depth_slice(
            params,
            scan_result["normalized_score_volume"],
            scan_result["best_location"],
            paths["figures"] / "fig_scan_x_depth_slice.png",
        )
        plot_scan_x_y_slice(
            params,
            scan_result["normalized_score_volume"],
            scan_result["best_location"],
            paths["figures"] / "fig_scan_x_y_slice.png",
        )
        plot_best_location_map(
            params,
            source_xyz,
            receiver_xyz,
            scan_result["best_location"],
            paths["figures"] / "fig_best_location_map.png",
        )

    if params.output.save_report:
        _write_scan_report(params, paths["reports"] / "report_scan.md", scan_result)

    metadata = build_metadata(
        params,
        synthetic_data,
        scatter_xyz,
        scatter_weight,
        font_info=font_info,
        wavefield_info=wavefield_info,
        scan_result=scan_result,
    )
    save_json(paths["metadata"] / "meta_run.json", metadata)

    scan_log = (
        "Stage 2 scan pipeline completed.\n"
        f"Score method: {params.scan.score_method}\n"
        f"Best location: {scan_result['best_location']}\n"
        f"Truth error: {scan_result['truth_error']}\n"
        "Warning: y-depth coupling may exist in single-sided DAS-like geometry.\n"
    )
    (paths["logs"] / "log_scan.txt").write_text(scan_log, encoding="utf-8")

    result = {"direct_times": direct_times, "scan_data": scan_data}
    result.update(scan_result)
    return result
