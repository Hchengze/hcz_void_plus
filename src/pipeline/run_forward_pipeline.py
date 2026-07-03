"""Stage 2 正演与中文可视化 pipeline。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np

from src.forward.multishot_forward import synthesize_multishot_forward
from src.geometry.acquisition_geometry import generate_receiver_xyz, generate_source_xyz
from src.model.anomalies import anomaly_to_scatter_points, build_anomaly_from_params
from src.model.velocity_model import build_velocity_model
from src.utils.metadata import build_metadata, save_json
from src.utils.path_manager import ensure_output_subdirs
from src.utils.random_seed import set_random_seed
from src.visualization.plot_gather import plot_shot_gather
from src.visualization.plot_geometry import plot_geometry, plot_geometry_layout_check
from src.visualization.plot_pseudo_wavefield import (
    save_pseudo_wavefield_animation,
    save_pseudo_wavefield_snapshots,
)
from src.visualization.plot_style import setup_chinese_matplotlib


def _write_forward_report(
    params: SimpleNamespace,
    output_path: Path,
    synthetic_data: np.ndarray,
    scatter_xyz: np.ndarray,
    snapshot_paths: list[Path],
    animation_info: dict[str, object],
    font_info: dict[str, object],
) -> None:
    """写出中文正演报告。"""

    animation_text = "成功" if animation_info.get("success") else f"未生成：{animation_info.get('reason')}"
    font_text = font_info.get("font_name") or font_info.get("warning") or "默认字体"
    content = f"""# 正演报告

## 本次运行

- task：`{params.project.task}`
- 数据形状：`{tuple(synthetic_data.shape)}`，维度顺序为 `shot × time × channel`
- DAS-like 接收级别：`{params.das_like.response_level}`
- 速度模型：`uniform effective Rayleigh velocity = {params.velocity.rayleigh_velocity_mps} m/s`
- 中文字体：`{font_text}`

## 当前近似条件

- 正演：`kinematic approximation`
- 接收：`DAS-like response approximation`
- 地表响应图：`kinematic_surface_response_snapshot`
- 运动学地表响应示意图和 GIF 只是 Rayleigh 波走时控制的地表响应示意，不是真实弹性波方程数值模拟。
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

    velocity_model = build_velocity_model(params)
    anomaly = build_anomaly_from_params(params)
    scatter_xyz, scatter_weight = anomaly_to_scatter_points(anomaly, params.anomaly.scatter_point_mode)

    forward_result = synthesize_multishot_forward(
        params=params,
        source_xyz=source_xyz,
        receiver_xyz=receiver_xyz,
        scatter_xyz=scatter_xyz,
        scatter_weight=scatter_weight,
        velocity_model=velocity_model,
    )
    synthetic_data = forward_result["synthetic_data"]

    if params.output.save_arrays:
        np.save(paths["arrays"] / "arr_synthetic_data.npy", synthetic_data)
        np.save(paths["arrays"] / "arr_time_axis.npy", params.derived.time_axis)
        np.save(paths["arrays"] / "arr_channel_x.npy", params.derived.channel_x)
        np.save(paths["arrays"] / "arr_shot_x.npy", params.derived.shot_x)

    if params.output.save_figures:
        plot_geometry(params, receiver_xyz, source_xyz, scatter_xyz, paths["figures"] / "fig_geometry.png")
        plot_geometry_layout_check(
            params,
            receiver_xyz,
            source_xyz,
            scatter_xyz,
            paths["figures"] / "fig_geometry_layout_check.png",
        )
        n_fig = min(params.output.max_shot_gather_figures, params.source.shot_count)
        for shot_index in range(n_fig):
            plot_shot_gather(params, synthetic_data, shot_index, paths["figures"] / f"fig_shot_gather_{shot_index:03d}.png")

    snapshot_paths = save_pseudo_wavefield_snapshots(
        params,
        source_xyz,
        scatter_xyz,
        scatter_weight,
        velocity_model.get_velocity(),
        paths["snapshots"],
    )
    animation_info = save_pseudo_wavefield_animation(
        params,
        source_xyz,
        scatter_xyz,
        scatter_weight,
        velocity_model.get_velocity(),
        paths["animations"] / "anim_pseudo_wavefield.gif",
    )
    wavefield_info = {
        "snapshot_count": len(snapshot_paths),
        "snapshot_files": [str(path) for path in snapshot_paths],
        "animation": animation_info,
    }

    metadata = build_metadata(params, synthetic_data, scatter_xyz, scatter_weight, font_info, wavefield_info)
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
        )

    log_text = (
        "Stage 2 forward pipeline completed.\n"
        "Approximation: kinematic approximation + DAS-like response approximation.\n"
        "Surface response: kinematic_surface_response_snapshot, not true elastic wave equation snapshot.\n"
        f"Output directory: {paths['root']}\n"
        f"Data shape: {synthetic_data.shape} (shot × time × channel)\n"
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
        "scatter_xyz": scatter_xyz,
        "scatter_weight": scatter_weight,
        "font_info": font_info,
        "wavefield_info": wavefield_info,
        "metadata": metadata,
    }
