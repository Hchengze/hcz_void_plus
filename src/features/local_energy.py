"""局部能量提取。"""

from __future__ import annotations

import numpy as np


def extract_window_energy(
    data: np.ndarray,
    time_axis: np.ndarray,
    target_times: np.ndarray,
    half_width_s: float,
) -> np.ndarray:
    """在目标走时附近提取局部能量。

    物理意义：
        绕射/散射能量如果与候选点理论走时对齐，则对应时间窗内的能量会较高。
        Stage 2 用这个最基础的局部能量作为扫描定位属性。

    输入参数：
        data：shape = (n_shot, n_time, n_channel)，即 shot × time × channel；
        time_axis：shape = (n_time,)，单位 s；
        target_times：shape = (n_shot, n_channel)，单位 s；
        half_width_s：时间窗半宽，单位 s。

    输出形状：
        energy，shape = (n_shot, n_channel)。

    边界处理：
        对越界时间窗自动截断；完全落在记录范围外时能量为 0，不会数组越界。
    """

    if data.ndim != 3:
        raise ValueError(f"data 维度错误：当前 shape={data.shape}，合理条件是 shot × time × channel。")
    n_shot, n_time, n_channel = data.shape
    if target_times.shape != (n_shot, n_channel):
        raise ValueError(f"target_times shape={target_times.shape}，应为 ({n_shot}, {n_channel})。")

    dt = float(time_axis[1] - time_axis[0]) if len(time_axis) > 1 else 1.0
    half_samples = int(np.ceil(half_width_s / dt))
    center_index = np.rint((target_times - time_axis[0]) / dt).astype(int)
    start = np.clip(center_index - half_samples, 0, n_time)
    stop = np.clip(center_index + half_samples + 1, 0, n_time)
    valid = stop > start

    energy_data = data * data
    cumulative = np.concatenate(
        [np.zeros((n_shot, 1, n_channel), dtype=float), np.cumsum(energy_data, axis=1)],
        axis=1,
    )
    shot_index = np.arange(n_shot)[:, None]
    channel_index = np.arange(n_channel)[None, :]
    energy = cumulative[shot_index, stop, channel_index] - cumulative[shot_index, start, channel_index]
    energy[~valid] = 0.0
    return energy
