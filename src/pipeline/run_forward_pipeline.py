"""Stage 5A 正演、三维几何诊断、速度模型与中文可视化 pipeline。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np

from src.forward.kinematic_volume_response import compute_kinematic_volume_response
from src.forward.forward_registry import get_forward_engine_spec, run_registered_forward
from src.geometry.acquisition_geometry import generate_receiver_xyz, generate_source_xyz
from src.model.anomalies import anomaly_to_scatter_points, build_anomaly_from_params
from src.utils.metadata import build_metadata, save_json
from src.utils.path_manager import ensure_output_subdirs
from src.utils.random_seed import set_random_seed
from src.visualization.animate_volume_wavefield import save_single_shot_volume_wavefield_animation
from src.visualization.plot_gather import plot_shot_gather
from src.visualization.plot_gather_with_velocity_model import (
    plot_shot_gather_attenuation_comparison,
    plot_shot_gather_uniform_vs_layered_overlay,
    plot_shot_gather_with_velocity_model,
)
from src.visualization.plot_geometry import (
    plot_3d_geometry_overview,
    plot_anomaly_3d_scatter_points,
    plot_geometry,
    plot_geometry_layout_check,
    plot_receiver_source_3d_layout,
)
from src.visualization.plot_pseudo_wavefield import (
    save_pseudo_wavefield_animation,
    save_pseudo_wavefield_snapshots,
)
from src.visualization.plot_style import setup_chinese_matplotlib
from src.visualization.plot_volume_wavefield import (
    plot_volume_wavefield_3d_energy_proxy,
    plot_volume_wavefield_depth_slices,
    plot_volume_wavefield_xyz_slices,
)


def _write_forward_report(
    params: SimpleNamespace,
    output_path: Path,
    synthetic_data: np.ndarray,
    scatter_xyz: np.ndarray,
    snapshot_paths: list[Path],
    animation_info: dict[str, object],
    font_info: dict[str, object],
    volume_response: dict[str, Any] | None,
    attenuation_summary: dict[str, object],
    gather_context: dict[str, object],
) -> None:
    """写出中文正演报告。"""

    animation_text = "成功" if animation_info.get("success") else f"未生成：{animation_info.get('reason')}"
    font_text = font_info.get("font_name") or font_info.get("warning") or "默认字体"
    content = f"""# 正演报告

## 本次运行

- task：`{params.project.task}`
- 数据形状：`{tuple(synthetic_data.shape)}`，维度顺序为 `shot × time × channel`
- forward engine：`{params.forward.engine}`
- DAS-like 接收级别：`{params.das_like.response_level}`
- 速度模型：`{params.velocity.model_type}`，代表速度 `{params.velocity.rayleigh_velocity_mps} m/s`
- 速度近似：`straight-ray kinematic approximation`，不是 3D elastic wavefield
- attenuation：enabled=`{attenuation_summary.get("attenuation_enabled")}`，q_default=`{attenuation_summary.get("q_default")}`
- attenuation RMS 差异：`{attenuation_summary.get("relative_rms_difference")}`（经验衰减，不是 viscoelastic wave equation）
- 三维体响应 proxy：`{None if volume_response is None else volume_response.get("metadata", {}).get("volume_grid_shape")}`
- 炮集速度模型叠加：`{gather_context.get("shot_gather_velocity_overlay_available")}`
- 中文字体：`{font_text}`

## 当前近似条件

- 正演：`kinematic approximation`
- 接收：`DAS-like response approximation`
- 三维体响应图：`3D kinematic volume response proxy`
- 运动学地表响应示意图和 GIF 只是 Rayleigh 波走时控制的地表响应示意，不是真实弹性波方程数值模拟。
- Stage 5J 新增 x-y-depth 体响应 proxy：depth 向下为正，走时使用 velocity_model path integration，振幅使用经验 Q attenuation。
- Rayleigh 深度敏感性：用 `exp(-h / penetration_depth)` 做简化衰减；这不是严格模态深度核。

## 异常体真值

- 类型：`{params.anomaly.anomaly_type}`
- 位置：x=`{params.anomaly.x0_m}` m，y=`{params.anomaly.y0_m}` m，h=`{params.anomaly.depth_m}` m
- 等效散射点数量：`{scatter_xyz.shape[0]}`
- 说明：多个散射点表示异常体形状是运动学等效散射近似，不是真实边界散射模拟。

## 几何自检

- DAS 光纤测线位于 y = `{params.fiber.y_m}` m。
- 震源测线位于 y = W = `{params.source.y_m}` m。
- 道路区域为 `0 <= y <= {params.road.width_m}` m。
- 异常体平面投影位于 x = `{params.anomaly.x0_m}` m，y = `{params.anomaly.y0_m}` m，埋深 h = `{params.anomaly.depth_m}` m。
- 当前伪波场快照为 x-y 表面平面运动学示意图，grid_z = 0。
- 异常体深度只参与三维路径距离计算，不作为 y 坐标显示。

## 输出

- 炮集图最大数量：`{params.output.max_shot_gather_figures}`
- 运动学地表响应示意图：`{len(snapshot_paths)}` 张
- 动图：{animation_text}

## 限制

当前结果不是完整 DAS 仪器模拟，不是完整三维弹性波全波场模拟，不能作为工程确诊结论。
"""
    output_path.write_text(content, encoding="utf-8")


def run_forward_pipeline(params: SimpleNamespace) -> dict[str, Any]:
    """运行 DAS-like 运动学多炮正演、中文图件和伪波场输出。"""

    set_random_seed(params)
    paths = ensure_output_subdirs(params)
    font_info = setup_chinese_matplotlib()

    receiver_xyz = generate_receiver_xyz(params)
    source_xyz = generate_source_xyz(params)
    params.derived.receiver_xyz = receiver_xyz
    params.derived.source_xyz = source_xyz

    anomaly = build_anomaly_from_params(params)
    scatter_xyz, scatter_weight = anomaly_to_scatter_points(anomaly, params.anomaly.scatter_point_mode)

    forward_result = run_registered_forward(
        params=params,
        source_xyz=source_xyz,
        receiver_xyz=receiver_xyz,
        scatter_xyz=scatter_xyz,
        scatter_weight=scatter_weight,
    )
    velocity_model = forward_result["velocity_model"]
    synthetic_data = forward_result["synthetic_data"]
    attenuation_summary = forward_result.get("attenuation_summary", {})
    observation_kernel_metadata = forward_result.get("observation_kernel_metadata", {})
    volume_response = None
    if params.output.volume_wavefield_enabled:
        volume_response = compute_kinematic_volume_response(
            params,
            source_xyz,
            scatter_xyz,
            scatter_weight,
            velocity_model,
        )

    if params.output.save_arrays:
        np.save(paths["arrays"] / "arr_synthetic_data.npy", synthetic_data)
        if forward_result.get("synthetic_data_no_attenuation") is not None:
            np.save(paths["arrays"] / "arr_synthetic_data_no_attenuation.npy", forward_result["synthetic_data_no_attenuation"])
        np.save(paths["arrays"] / "arr_time_axis.npy", params.derived.time_axis)
        np.save(paths["arrays"] / "arr_channel_x.npy", params.derived.channel_x)
        np.save(paths["arrays"] / "arr_shot_x.npy", params.derived.shot_x)
        if volume_response is not None:
            np.save(paths["arrays"] / "arr_volume_wavefield_frames.npy", volume_response["volume_frames"])
            np.save(paths["arrays"] / "arr_volume_wavefield_energy.npy", volume_response["energy_volume"])
            np.save(paths["arrays"] / "arr_volume_wavefield_x.npy", volume_response["x_axis_m"])
            np.save(paths["arrays"] / "arr_volume_wavefield_y.npy", volume_response["y_axis_m"])
            np.save(paths["arrays"] / "arr_volume_wavefield_depth.npy", volume_response["depth_axis_m"])

    gather_context: dict[str, object] = {}
    if params.output.save_figures:
        plot_geometry(params, receiver_xyz, source_xyz, scatter_xyz, paths["figures"] / "fig_geometry.png")
        plot_geometry_layout_check(
            params,
            receiver_xyz,
            source_xyz,
            scatter_xyz,
            paths["figures"] / "fig_geometry_layout_check.png",
        )
        plot_receiver_source_3d_layout(params, receiver_xyz, source_xyz, paths["figures"] / "fig_receiver_source_3d_layout.png")
        plot_anomaly_3d_scatter_points(params, scatter_xyz, paths["figures"] / "fig_anomaly_3d_scatter_points.png")
        plot_3d_geometry_overview(params, receiver_xyz, source_xyz, scatter_xyz, paths["figures"] / "fig_3d_geometry_overview.png")
        n_fig = min(params.output.max_shot_gather_figures, params.source.shot_count)
        for shot_index in range(n_fig):
            plot_shot_gather(params, synthetic_data, shot_index, paths["figures"] / f"fig_shot_gather_{shot_index:03d}.png")
        gather_context.update(
            plot_shot_gather_with_velocity_model(
                params,
                synthetic_data,
                0,
                source_xyz,
                receiver_xyz,
                scatter_xyz,
                velocity_model,
                paths["figures"] / "fig_shot_gather_with_velocity_model.png",
            )
        )
        gather_context.update(
            plot_shot_gather_uniform_vs_layered_overlay(
                params,
                synthetic_data,
                0,
                source_xyz,
                receiver_xyz,
                scatter_xyz,
                velocity_model,
                paths["figures"] / "fig_shot_gather_uniform_vs_layered_overlay.png",
            )
        )
        gather_context.update(
            plot_shot_gather_attenuation_comparison(
                params,
                synthetic_data,
                forward_result.get("synthetic_data_no_attenuation"),
                0,
                paths["figures"] / "fig_shot_gather_attenuation_comparison.png",
            )
        )
        if volume_response is not None:
            plot_volume_wavefield_xyz_slices(params, volume_response, paths["figures"] / "fig_volume_wavefield_xyz_slices.png")
            plot_volume_wavefield_depth_slices(params, volume_response, paths["figures"] / "fig_volume_wavefield_depth_slices.png")
            plot_volume_wavefield_3d_energy_proxy(params, volume_response, paths["figures"] / "fig_volume_wavefield_3d_energy_proxy.png")

    snapshot_paths = save_pseudo_wavefield_snapshots(
        params,
        source_xyz,
        scatter_xyz,
        scatter_weight,
        velocity_model,
        paths["snapshots"],
    )
    animation_info = save_pseudo_wavefield_animation(
        params,
        source_xyz,
        scatter_xyz,
        scatter_weight,
        velocity_model,
        paths["animations"] / "anim_pseudo_wavefield.gif",
    )
    volume_animation_info = (
        save_single_shot_volume_wavefield_animation(
            params,
            volume_response,
            paths["animations"] / "anim_single_shot_volume_wavefield.gif",
        )
        if volume_response is not None
        else {"success": False, "path": None, "reason": "volume_wavefield_enabled=False"}
    )
    wavefield_info = {
        "snapshot_count": len(snapshot_paths),
        "snapshot_files": [str(path) for path in snapshot_paths],
        "animation": animation_info,
        "volume_response": None if volume_response is None else volume_response["metadata"],
        "volume_animation": volume_animation_info,
    }

    metadata = build_metadata(
        params,
        synthetic_data,
        scatter_xyz,
        scatter_weight,
        font_info,
        wavefield_info,
        forward_info={
            "forward_engine": forward_result.get("forward_engine", params.forward.engine),
            "forward_stage": forward_result.get("forward_stage"),
            "observation_kernel_3d": observation_kernel_metadata,
            "forward_uses_observation_kernel": bool(observation_kernel_metadata.get("forward_uses_observation_kernel")),
            "note": "Stage 5K 当前主流程 forward 为 layered_kinematic straight-ray kinematic approximation；正演和定位优先共享 3D observation kernel，x-y-depth 体响应 proxy 只用于可视化，不是 3D elastic wavefield。",
        },
    )
    save_json(paths["metadata"] / "params_snapshot.json", params)
    save_json(paths["metadata"] / "meta_run.json", metadata)

    if params.output.save_report:
        _write_forward_report(
            params,
            paths["reports"] / "report_forward.md",
            synthetic_data,
            scatter_xyz,
            snapshot_paths,
            animation_info,
            font_info,
            volume_response,
            attenuation_summary,
            gather_context,
        )

    log_text = (
        "Stage 5K forward pipeline completed.\n"
        "Approximation: kinematic approximation + DAS-like response approximation.\n"
        "Observation kernel: shared 3D source-candidate-receiver path table for forward/localization.\n"
        "Volume response: visualization_only 3D kinematic proxy, not receiver-consistent imaging and not true elastic wave equation snapshot.\n"
        f"Output directory: {paths['root']}\n"
        f"Data shape: {synthetic_data.shape} (shot × time × channel)\n"
        f"Volume shape: {None if volume_response is None else volume_response['metadata']['volume_grid_shape']}\n"
        f"Attenuation enabled: {params.attenuation.enabled}\n"
        f"Forward uses observation kernel: {bool(observation_kernel_metadata.get('forward_uses_observation_kernel'))}\n"
    )
    (paths["logs"] / "log_run.txt").write_text(log_text, encoding="utf-8")

    return {
        "paths": paths,
        "output_run_dir": str(paths["root"]),
        "synthetic_data": synthetic_data,
        "synthetic_data_shape": synthetic_data.shape,
        "receiver_xyz": receiver_xyz,
        "source_xyz": source_xyz,
        "velocity_model": velocity_model,
        "forward_engine": forward_result.get("forward_engine", params.forward.engine),
        "forward_stage": forward_result.get("forward_stage", get_forward_engine_spec(params.forward.engine).stage),
        "scatter_xyz": scatter_xyz,
        "scatter_weight": scatter_weight,
        "synthetic_data_no_attenuation": forward_result.get("synthetic_data_no_attenuation"),
        "attenuation_summary": attenuation_summary,
        "observation_paths_3d": forward_result.get("observation_paths_3d"),
        "observation_kernel_metadata": observation_kernel_metadata,
        "volume_response": volume_response,
        "volume_response_metadata": None if volume_response is None else volume_response["metadata"],
        "gather_velocity_context": gather_context,
        "font_info": font_info,
        "wavefield_info": wavefield_info,
        "metadata": metadata,
    }
