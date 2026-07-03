"""Stage 1 正演 pipeline。"""

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
from src.visualization.plot_geometry import plot_geometry


def _write_forward_report(
    params: SimpleNamespace,
    output_path: Path,
    synthetic_data: np.ndarray,
    scatter_xyz: np.ndarray,
) -> None:
    """写出简要 Markdown 报告。"""

    content = f"""# Forward Report

本报告由 hcz_void_plus Stage 1 自动生成。

## 数据形状

- synthetic_data shape: `{tuple(synthetic_data.shape)}`
- 维度顺序: `shot × time × channel`
- n_shot: `{params.source.shot_count}`
- n_time: `{params.derived.nt}`
- n_channel: `{params.fiber.channel_count}`

## 当前近似

- forward: `kinematic approximation`
- DAS-like: `DAS-like response approximation`
- receiver: `point_receiver approximation`
- velocity: `uniform effective Rayleigh velocity`

## 重要限制

当前结果不是完整 DAS 仪器模拟，也不是完整三维弹性波全波场模拟。gauge length 参数已经进入统一参数中心和 metadata，但在 point receiver 模式下不参与波形计算。本结果用于科研算法原型调试，不能作为工程确诊结论。

## 异常体与散射点

- anomaly type: `{params.anomaly.anomaly_type}`
- scatter point mode: `{params.anomaly.scatter_point_mode}`
- scatter point count: `{scatter_xyz.shape[0]}`
- note: 多个散射点表示异常体形状是运动学等效散射近似，不是真实边界散射模拟。

## 后续阶段

scan、confidence、robustness、多炮联合定位、DAS gauge length 响应增强、分层速度模型和局部全波场验证将在后续阶段实现。
"""
    output_path.write_text(content, encoding="utf-8")


def run_forward_pipeline(params: SimpleNamespace) -> dict[str, Any]:
    """运行最小 DAS-like 运动学正演闭环。

    步骤：
        1. 设置随机种子；
        2. 生成几何；
        3. 构建速度模型；
        4. 构建异常体和散射点；
        5. 生成多炮 DAS-like 合成数据；
        6. 保存数组；
        7. 保存 params snapshot 和 metadata；
        8. 绘制几何图和若干炮集图；
        9. 输出简要 Markdown 报告和日志。
    """

    set_random_seed(params)
    paths = ensure_output_subdirs(params)

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

    save_json(paths["root"] / "params_snapshot.json", params)
    metadata = build_metadata(params, synthetic_data, scatter_xyz, scatter_weight)
    save_json(paths["root"] / "metadata.json", metadata)

    if params.output.save_arrays:
        np.save(paths["arrays"] / "synthetic_data.npy", synthetic_data)
        np.save(paths["arrays"] / "time_axis.npy", params.derived.time_axis)
        np.save(paths["arrays"] / "channel_x.npy", params.derived.channel_x)
        np.save(paths["arrays"] / "shot_x.npy", params.derived.shot_x)

    if params.output.save_figures:
        plot_geometry(params, receiver_xyz, source_xyz, scatter_xyz, paths["figures"] / "geometry.png")
        n_fig = min(params.task.max_shot_figures, params.source.shot_count)
        for shot_index in range(n_fig):
            plot_shot_gather(params, synthetic_data, shot_index, paths["figures"] / f"shot_gather_{shot_index:03d}.png")

    if params.output.save_report:
        _write_forward_report(params, paths["reports"] / "forward_report.md", synthetic_data, scatter_xyz)

    log_text = (
        "Stage 1 forward pipeline completed.\n"
        "Approximation: kinematic approximation + DAS-like response approximation.\n"
        f"Output directory: {paths['root']}\n"
        f"Data shape: {synthetic_data.shape} (shot × time × channel)\n"
    )
    (paths["logs"] / "run_log.txt").write_text(log_text, encoding="utf-8")

    return {
        "output_run_dir": str(paths["root"]),
        "synthetic_data_shape": synthetic_data.shape,
        "metadata": metadata,
    }
