"""Stage 4A 预处理、多属性扫描定位与诊断图件 pipeline。"""

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
from src.preprocessing.preprocessing_pipeline import run_preprocessing_pipeline
from src.utils.metadata import build_metadata, save_json
from src.utils.path_manager import ensure_output_subdirs
from src.visualization.plot_physical_diagnostics import (
    plot_diffraction_travel_time_curves,
    plot_rayleigh_depth_sensitivity,
    plot_source_anomaly_receiver_path_section,
)
from src.visualization.plot_preprocessing import plot_preprocessing_comparison
from src.visualization.plot_scan import (
    plot_best_location_map,
    plot_raw_vs_weighted_best_location,
    plot_raw_vs_weighted_x_depth_slice,
    plot_scan_x_depth_slice,
    plot_scan_x_y_slice,
)


def _write_scan_report(params: SimpleNamespace, output_path: Path, scan_result: dict[str, Any]) -> None:
    """写出中文扫描定位报告。"""

    best = scan_result["best_location"]
    error = scan_result["truth_error"]
    unweighted_best = scan_result["unweighted_best_location"]
    weighted_best = scan_result["weighted_best_location"]
    diff = scan_result["raw_weighted_difference"]
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
- arr_score_volume.npy 当前展示主结果：`{scan_result["score_volume_kind"]}`
- depth weighting：`{params.scan.use_depth_weight}`
- Rayleigh 波长估计：`{params.derived.estimated_wavelength_m:.3f}` m
- Rayleigh 穿透深度近似：`{scan_result["penetration_depth_m"]:.3f}` m

## 预处理

- preprocess_enabled：`{params.preprocessing.enabled}`
- bandpass：`{params.preprocessing.bandpass_enabled}`，`{params.preprocessing.bandpass_low_hz}`-`{params.preprocessing.bandpass_high_hz}` Hz
- AGC：`{params.preprocessing.agc_enabled}`
- envelope：`{params.preprocessing.envelope_enabled}`
- trace_normalization：`{params.preprocessing.trace_normalization}`
- FK filter：`{params.preprocessing.fk_filter_enabled}`

## 结果

- best_location：x=`{best["x_m"]}` m，y=`{best["y_m"]}` m，h=`{best["depth_m"]}` m
- best_score：`{scan_result["best_score"]}`
- truth_error：dx=`{error["dx_m"]}` m，dy=`{error["dy_m"]}` m，dh=`{error["ddepth_m"]}` m，三维距离=`{error["distance_m"]}` m

## unweighted 与 weighted best 分离

- unweighted_best：x=`{unweighted_best["x_m"]}` m，y=`{unweighted_best["y_m"]}` m，h=`{unweighted_best["depth_m"]}` m，score=`{scan_result["unweighted_best_score"]}`
- weighted_best：x=`{weighted_best["x_m"]}` m，y=`{weighted_best["y_m"]}` m，h=`{weighted_best["depth_m"]}` m，score=`{scan_result["weighted_best_score"]}`
- unweighted -> weighted 差异：dx=`{diff["dx_m"]}` m，dy=`{diff["dy_m"]}` m，dh=`{diff["ddepth_m"]}` m，三维距离=`{diff["distance_m"]}` m
- depth_prior_bias_warning：`{scan_result["depth_prior_bias_warning"]}`

## 风险提示

{scan_result["y_depth_coupling_warning"]}

## 物理自检

- 当前地表响应图是 Rayleigh 波走时控制的运动学地表响应示意，不是真实弹性波场快照。
- Rayleigh 波能量主要集中在地表附近，本轮用 `exp(-h / penetration_depth)` 作为简化深度敏感性权重。
- 该权重不是严格 Rayleigh 模态深度核，只用于避免深部候选点在运动学扫描中被不合理高估。
- 绕射走时曲线图用于检查理论散射走时是否与炮集上的能量事件大致对应。
- 单侧 DAS-like 几何下 y-depth 耦合仍然存在，best_location 只是科研级候选位置。
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
    processed_data, preprocessing_info = run_preprocessing_pipeline(synthetic_data, params)
    scan_data = processed_data
    if params.scan.direct_mute_enabled:
        scan_data = mute_direct_wave(
            scan_data,
            params.derived.time_axis,
            direct_times,
            params.scan.direct_mute_half_width_s,
            mode=params.scan.direct_mute_mode,
        )

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
        np.save(paths["arrays"] / "arr_score_volume_active.npy", scan_result["score_volume_active"])
        np.save(paths["arrays"] / "arr_score_volume_unweighted.npy", scan_result["score_volume_unweighted"])
        np.save(paths["arrays"] / "arr_score_volume_raw.npy", scan_result["score_volume_raw"])
        np.save(paths["arrays"] / "arr_score_volume_depth_weighted.npy", scan_result["score_volume_depth_weighted"])
        for name, volume in scan_result.get("attribute_score_volumes", {}).items():
            np.save(paths["arrays"] / f"arr_{name}.npy", volume)
        np.save(paths["arrays"] / "arr_scan_x_grid.npy", params.derived.scan_x_grid)
        np.save(paths["arrays"] / "arr_scan_y_grid.npy", params.derived.scan_y_grid)
        np.save(paths["arrays"] / "arr_scan_depth_grid.npy", params.derived.scan_depth_grid)
        np.save(paths["arrays"] / "arr_direct_times.npy", direct_times)
        np.save(paths["arrays"] / "arr_processed_data.npy", processed_data)

    if params.output.save_figures:
        plot_scan_x_depth_slice(
            params,
            scan_result["normalized_score_volume"],
            scan_result["best_location"],
            paths["figures"] / "fig_scan_x_depth_slice.png",
        )
        plot_preprocessing_comparison(
            params,
            synthetic_data,
            processed_data,
            paths["figures"] / "fig_preprocessing_comparison.png",
            shot_index=min(params.output.wavefield_shot_index, synthetic_data.shape[0] - 1),
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
        plot_raw_vs_weighted_best_location(
            params,
            source_xyz,
            receiver_xyz,
            scan_result,
            paths["figures"] / "fig_raw_vs_weighted_best_location.png",
        )
        plot_raw_vs_weighted_x_depth_slice(
            params,
            scan_result,
            paths["figures"] / "fig_raw_vs_weighted_x_depth_slice.png",
        )
        plot_source_anomaly_receiver_path_section(
            params,
            source_xyz,
            receiver_xyz,
            paths["figures"] / "fig_source_anomaly_receiver_path_section.png",
        )
        plot_rayleigh_depth_sensitivity(
            params,
            paths["figures"] / "fig_rayleigh_depth_sensitivity.png",
        )
        plot_diffraction_travel_time_curves(
            params,
            scan_data,
            source_xyz,
            receiver_xyz,
            velocity_model,
            scan_result["best_location"],
            paths["figures"] / "fig_diffraction_travel_time_curves.png",
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
        diagnostics_info={
            "diffraction_travel_time_curve_figure": str(paths["figures"] / "fig_diffraction_travel_time_curves.png"),
            "path_section_figure": str(paths["figures"] / "fig_source_anomaly_receiver_path_section.png"),
            "depth_sensitivity_figure": str(paths["figures"] / "fig_rayleigh_depth_sensitivity.png"),
            "raw_vs_weighted_best_location_figure": str(paths["figures"] / "fig_raw_vs_weighted_best_location.png"),
            "raw_vs_weighted_x_depth_slice_figure": str(paths["figures"] / "fig_raw_vs_weighted_x_depth_slice.png"),
            "preprocessing_comparison_figure": str(paths["figures"] / "fig_preprocessing_comparison.png"),
        },
    )
    save_json(paths["metadata"] / "meta_run.json", metadata)

    scan_log = (
        "Stage 4A scan pipeline completed.\n"
        f"Score method: {params.scan.score_method}\n"
        f"Best location: {scan_result['best_location']}\n"
        f"Truth error: {scan_result['truth_error']}\n"
        f"Preprocessing: {preprocessing_info}\n"
        "Warning: y-depth coupling may exist in single-sided DAS-like geometry.\n"
    )
    (paths["logs"] / "log_scan.txt").write_text(scan_log, encoding="utf-8")

    result = {"direct_times": direct_times, "scan_data": scan_data, "processed_data": processed_data, "preprocessing_info": preprocessing_info}
    result.update(scan_result)
    return result
