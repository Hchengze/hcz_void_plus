"""直达波 mute。"""

from __future__ import annotations

import numpy as np


def mute_direct_wave(
    data: np.ndarray,
    time_axis: np.ndarray,
    direct_times: np.ndarray,
    half_width_s: float,
    mode: str = "taper",
) -> np.ndarray:
    """按预测直达波到时时间窗压制直达面波。

    物理意义：
        直达瑞雷波通常能量强，会掩盖异常体弱散射/绕射能量。Stage 2 使用简单
        时间窗 mute，为基础扫描定位提供更干净的局部能量属性。Stage 3B 默认改为
        taper 模式：窗口中心强衰减，窗口边界用余弦函数平滑过渡，避免硬置零在
        时间窗边缘产生不自然突变。

    输入参数：
        data：shape = (n_shot, n_time, n_channel)，即 shot × time × channel；
        direct_times：shape = (n_shot, n_channel)，单位 s；
        half_width_s：mute 半窗宽，单位 s。
        mode：
            "taper"：余弦窗平滑衰减，默认；
            "hard"：窗口内硬置零，用于对比旧流程；
            "subtract"：用同一 taper 权重减去直达波窗内样值，保留接口用于后续改进；
            "none"：不压制，直接返回复制数据。

    输出形状：
        muted_data，与 data 同 shape。

    近似条件和限制：
        这是基于预测直达走时的局部时间窗处理，不是自适应面波分离，也不是完整
        波场分解。subtract 模式当前只是局部窗口内的简化扣除，不代表真实直达波建模。
    """

    if mode not in {"hard", "taper", "subtract", "none"}:
        raise ValueError(f"direct mute mode 错误：当前值为 {mode}，合理选项是 hard/taper/subtract/none。")
    muted = data.copy()
    if half_width_s == 0 or mode == "none":
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
                if mode == "hard":
                    muted[i_shot, start:stop, i_channel] = 0.0
                    continue

                sample_index = np.arange(start, stop, dtype=float)
                distance_from_center = np.abs(sample_index - center_index[i_shot, i_channel])
                normalized_distance = np.clip(distance_from_center / max(half_samples, 1), 0.0, 1.0)
                # attenuation 在中心为 0，在窗口边界平滑回到 1。这样不会像 hard mute
                # 那样在 start/stop 处制造突变边界，更适合作为默认科研 QC 流程。
                attenuation = 0.5 - 0.5 * np.cos(np.pi * normalized_distance)
                if mode == "taper":
                    muted[i_shot, start:stop, i_channel] *= attenuation
                elif mode == "subtract":
                    direct_estimate = data[i_shot, start:stop, i_channel] * (1.0 - attenuation)
                    muted[i_shot, start:stop, i_channel] -= direct_estimate
    return muted
