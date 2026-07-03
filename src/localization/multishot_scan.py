"""x-y-h 多炮基础扫描定位。"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from src.localization.travel_time import compute_candidate_diffraction_times
from src.model.velocity_model import UniformVelocityModel
from src.physics.rayleigh import estimate_penetration_depth, rayleigh_depth_weight


def _build_energy_cumulative(data: np.ndarray) -> np.ndarray:
    """预计算 data^2 沿时间轴的累计和，用于快速窗口能量查询。"""

    energy_data = data * data
    return np.concatenate(
        [np.zeros((data.shape[0], 1, data.shape[2]), dtype=float), np.cumsum(energy_data, axis=1)],
        axis=1,
    )


def _score_candidate_fast(
    cumulative_energy: np.ndarray,
    time_axis: np.ndarray,
    candidate_times: np.ndarray,
    half_width_s: float,
) -> float:
    """用预计算累计能量快速计算候选点得分。

    candidate_times 的 shape 为 shot × channel。通过累计和查询窗口能量，避免对
    每个候选点重复扫描完整 time 轴。
    """

    n_shot = cumulative_energy.shape[0]
    n_time = cumulative_energy.shape[1] - 1
    n_channel = cumulative_energy.shape[2]
    dt = float(time_axis[1] - time_axis[0]) if len(time_axis) > 1 else 1.0
    half_samples = int(np.ceil(half_width_s / dt))
    center_index = np.rint((candidate_times - time_axis[0]) / dt).astype(int)
    start = np.clip(center_index - half_samples, 0, n_time)
    stop = np.clip(center_index + half_samples + 1, 0, n_time)
    valid = stop > start
    shot_index = np.arange(n_shot)[:, None]
    channel_index = np.arange(n_channel)[None, :]
    energy = cumulative_energy[shot_index, stop, channel_index] - cumulative_energy[shot_index, start, channel_index]
    energy[~valid] = 0.0
    return float(np.mean(energy))


def run_multishot_scan(
    data: np.ndarray,
    time_axis: np.ndarray,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    velocity_model: UniformVelocityModel,
    scan_grid: dict[str, Any],
    params: SimpleNamespace,
) -> dict[str, Any]:
    """运行基础 x-y-h 多炮扫描定位。

    扫描逻辑：
        1. 遍历候选异常体位置 x-y-h 网格；
        2. 计算 source -> candidate -> receiver 理论散射走时；
        3. 在 DAS-like 数据中沿该走时时间窗提取局部能量；
        4. 对所有 shot 和 channel 求平均，得到候选点 score；
        5. 形成 score_volume，shape = n_x, n_y, n_depth；
        6. 最高得分位置作为 best_location，并计算与单异常体真值的距离误差。

    限制：
        当前是基于运动学等效散射和局部能量聚焦的基础扫描，不是 FWI，不是完整
        成像，也不能作为工程确诊。单侧 DAS 几何下 y-depth 可能存在耦合。
    """

    x_grid = scan_grid["x_grid"]
    y_grid = scan_grid["y_grid"]
    depth_grid = scan_grid["depth_grid"]
    score_volume_raw = np.zeros((len(x_grid), len(y_grid), len(depth_grid)), dtype=float)
    cumulative_energy = _build_energy_cumulative(data)
    penetration_depth_m = estimate_penetration_depth(params)

    for ix, x_m in enumerate(x_grid):
        for iy, y_m in enumerate(y_grid):
            for iz, depth_m in enumerate(depth_grid):
                candidate_xyz = np.array([x_m, y_m, depth_m], dtype=float)
                candidate_times = compute_candidate_diffraction_times(
                    candidate_xyz, source_xyz, receiver_xyz, velocity_model, t0_s=params.time.t0_s
                )
                score_volume_raw[ix, iy, iz] = _score_candidate_fast(
                    cumulative_energy, time_axis, candidate_times, params.scan.time_window_half_width_s
                )

    depth_weights = rayleigh_depth_weight(depth_grid, penetration_depth_m)
    score_volume_depth_weighted = score_volume_raw * depth_weights[None, None, :]
    score_volume = score_volume_depth_weighted if params.scan.use_depth_weight else score_volume_raw

    best_index = np.unravel_index(int(np.argmax(score_volume)), score_volume.shape)
    best_location = {
        "x_m": float(x_grid[best_index[0]]),
        "y_m": float(y_grid[best_index[1]]),
        "depth_m": float(depth_grid[best_index[2]]),
    }
    truth = np.array([params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m], dtype=float)
    best = np.array([best_location["x_m"], best_location["y_m"], best_location["depth_m"]], dtype=float)
    truth_error = {
        "dx_m": float(best[0] - truth[0]),
        "dy_m": float(best[1] - truth[1]),
        "ddepth_m": float(best[2] - truth[2]),
        "distance_m": float(np.linalg.norm(best - truth)),
    }

    max_score = float(np.max(score_volume))
    min_score = float(np.min(score_volume))
    if max_score > min_score:
        normalized_score_volume = (score_volume - min_score) / (max_score - min_score)
    else:
        normalized_score_volume = np.zeros_like(score_volume)

    return {
        "score_volume": score_volume,
        "score_volume_raw": score_volume_raw,
        "score_volume_depth_weighted": score_volume_depth_weighted,
        "depth_weights": depth_weights,
        "depth_weight_enabled": params.scan.use_depth_weight,
        "penetration_depth_m": penetration_depth_m,
        "normalized_score_volume": normalized_score_volume,
        "best_index": best_index,
        "best_location": best_location,
        "best_score": float(score_volume[best_index]),
        "truth_error": truth_error,
        "y_depth_coupling_warning": "单侧 DAS-like 几何下，横向 y 与埋深 h 可能存在耦合，best_location 不能作为工程确诊。",
    }
