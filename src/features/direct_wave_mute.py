"""直达波 mute。"""

from __future__ import annotations

import numpy as np


def mute_direct_wave(
    data: np.ndarray,
    time_axis: np.ndarray,
    direct_times: np.ndarray,
    half_width_s: float,
) -> np.ndarray:
    """按预测直达波到时时间窗将数据置零。

    物理意义：
        直达瑞雷波通常能量强，会掩盖异常体弱散射/绕射能量。Stage 2 使用简单
        时间窗 mute，为基础扫描定位提供更干净的局部能量属性。

    输入参数：
        data：shape = (n_shot, n_time, n_channel)，即 shot × time × channel；
        direct_times：shape = (n_shot, n_channel)，单位 s；
        half_width_s：mute 半窗宽，单位 s。

    输出形状：
        muted_data，与 data 同 shape。

    近似条件和限制：
        这是最简单的硬置零 mute，不是自适应滤波，也不是完整面波压制算法。
    """

    muted = data.copy()
    if half_width_s == 0:
        return muted
    n_shot, n_time, n_channel = data.shape
    dt = float(time_axis[1] - time_axis[0]) if len(time_axis) > 1 else 1.0
    half_samples = int(np.ceil(half_width_s / dt))
    center_index = np.rint((direct_times - time_axis[0]) / dt).astype(int)

    for i_shot in range(n_shot):
        for i_channel in range(n_channel):
            start = max(0, center_index[i_shot, i_channel] - half_samples)
            stop = min(n_time, center_index[i_shot, i_channel] + half_samples + 1)
            if stop > start:
                muted[i_shot, start:stop, i_channel] = 0.0
    return muted
