"""多属性定位评分。

本模块把 Stage 4A 的轻量占位属性升级为可验证的运动学属性：

1. energy_score：沿候选绕射走时曲线提取局部能量；
2. normalized_energy_score：按每道总能量归一化后的局部能量；
3. matched_wavelet_score：局部窗口与 Ricker 子波模板的去均值归一化相关；
4. semblance_score：对齐窗口之间的波形一致性；
5. frequency_shift_score：候选窗口相对背景窗口的谱质心下降诊断。

所有函数仍服务于 DAS-like response approximation 与 kinematic approximation，
不是完整 DAS 仪器响应，也不是三维弹性波成像。
"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.forward.wavelet import ricker


EPS = 1.0e-12


def _window_energy(
    cumulative_energy: np.ndarray,
    center_index: np.ndarray,
    half_samples: int,
) -> tuple[np.ndarray, np.ndarray]:
    """用时间累积能量快速提取每个 shot-channel 的局部窗口能量。

    参数
    ----
    cumulative_energy:
        shape = ``shot x (time + 1) x channel``，由 ``data**2`` 沿时间轴累加得到。
    center_index:
        shape = ``shot x channel``，候选绕射走时对应的采样点索引。
    half_samples:
        时间窗半宽，单位为采样点。

    返回
    ----
    energy:
        shape = ``shot x channel``，每条理论绕射曲线附近的局部能量。
    valid:
        shape = ``shot x channel``，表示窗口是否至少覆盖一个有效采样点。
    """

    n_shot = cumulative_energy.shape[0]
    n_time = cumulative_energy.shape[1] - 1
    n_channel = cumulative_energy.shape[2]
    start = np.clip(center_index - half_samples, 0, n_time)
    stop = np.clip(center_index + half_samples + 1, 0, n_time)
    valid = stop > start
    shot_index = np.arange(n_shot)[:, None]
    channel_index = np.arange(n_channel)[None, :]
    energy = cumulative_energy[shot_index, stop, channel_index] - cumulative_energy[shot_index, start, channel_index]
    energy[~valid] = 0.0
    return energy, valid


def _candidate_center_indices(time_axis: np.ndarray, candidate_times: np.ndarray) -> tuple[np.ndarray, float]:
    """把候选理论走时转换为采样点索引。"""

    dt = float(time_axis[1] - time_axis[0]) if len(time_axis) > 1 else 1.0
    center_index = np.rint((candidate_times - time_axis[0]) / dt).astype(int)
    return center_index, dt


def extract_aligned_windows(
    data: np.ndarray,
    time_axis: np.ndarray,
    candidate_times: np.ndarray,
    half_width_s: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """沿候选绕射走时曲线截取并对齐局部波形窗口。

    物理意义
    --------
    对一个候选三维异常点，理论走时 ``source -> candidate -> receiver`` 会在
    每个 shot-channel 上给出一个到时。若候选点正确，绕射/散射能量应在这些
    到时附近出现。该函数把所有 shot-channel 的局部窗口对齐到同一个中心，
    供 matched wavelet 和 semblance 属性使用。

    输入
    ----
    data:
        DAS-like 数据，shape = ``shot x time x channel``。
    candidate_times:
        理论绕射走时，shape = ``shot x channel``，单位 s。
    half_width_s:
        局部窗口半宽，单位 s。

    输出
    ----
    windows:
        shape = ``n_valid_trace x n_window_sample``，每行是一个对齐窗口。
        越界部分用 0 填充；完全越界的窗口会被标记为 invalid。
    valid:
        shape = ``n_valid_trace``，表示每行是否含有足够有效样点。
    sample_offsets_s:
        shape = ``n_window_sample``，窗口内相对中心的时间轴，单位 s。
    """

    n_shot, n_time, n_channel = data.shape
    center_index, dt = _candidate_center_indices(time_axis, candidate_times)
    half_samples = int(np.ceil(half_width_s / dt))
    sample_offsets = np.arange(-half_samples, half_samples + 1, dtype=int)
    sample_offsets_s = sample_offsets.astype(float) * dt
    n_window = len(sample_offsets)

    # 这里必须向量化。默认三维扫描会对数千个候选点重复调用该函数；
    # 若在 Python 层逐 shot、逐 channel 循环，full_pipeline 会明显变慢。
    # indices 的 shape = shot x channel x window_sample。
    indices = center_index[:, :, None] + sample_offsets[None, None, :]
    in_bounds = (indices >= 0) & (indices < n_time)
    clipped = np.clip(indices, 0, n_time - 1)
    shot_index = np.arange(n_shot)[:, None, None]
    channel_index = np.arange(n_channel)[None, :, None]
    windows_3d = data[shot_index, clipped, channel_index]
    windows_3d = np.where(in_bounds, windows_3d, 0.0)
    valid_2d = np.count_nonzero(in_bounds, axis=2) >= max(3, n_window // 3)
    return windows_3d.reshape(n_shot * n_channel, n_window), valid_2d.ravel(), sample_offsets_s


def normalized_correlation_with_template(windows: np.ndarray, template: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """计算每个窗口与模板的去均值归一化相关系数。

    该函数是 matched_wavelet_score 的核心。它不会假设振幅大小，只看局部
    波形是否像 Ricker 子波，因此比单纯能量对强直达波残留更稳健。
    """

    if windows.size == 0:
        return np.zeros(0, dtype=float)
    centered_template = template - np.mean(template)
    template_norm = float(np.linalg.norm(centered_template))
    if template_norm <= EPS:
        return np.zeros(windows.shape[0], dtype=float)

    centered = windows - np.mean(windows, axis=1, keepdims=True)
    norms = np.linalg.norm(centered, axis=1) * template_norm
    corr = np.zeros(windows.shape[0], dtype=float)
    usable = valid & (norms > EPS)
    corr[usable] = (centered[usable] @ centered_template) / norms[usable]
    return corr


def compute_matched_wavelet_score(
    data: np.ndarray,
    time_axis: np.ndarray,
    candidate_times: np.ndarray,
    half_width_s: float,
    frequency_hz: float,
) -> float:
    """计算候选点的 Ricker 模板匹配得分。

    得分定义为全部有效 shot-channel 局部窗口与 Ricker 模板相关系数的稳健
    平均。这里使用绝对相关值的 75% 分位数，目的是降低少量异常道对得分的
    支配，同时允许散射极性在简化模型中存在翻转。
    """

    windows, valid, sample_offsets_s = extract_aligned_windows(data, time_axis, candidate_times, half_width_s)
    if not np.any(valid):
        return 0.0
    template = ricker(sample_offsets_s, frequency_hz)
    corr = normalized_correlation_with_template(windows, template, valid)
    valid_corr = np.abs(corr[valid])
    if valid_corr.size == 0:
        return 0.0
    return float(np.percentile(valid_corr, 75.0))


def compute_semblance_score(
    data: np.ndarray,
    time_axis: np.ndarray,
    candidate_times: np.ndarray,
    half_width_s: float,
) -> float:
    """计算沿候选绕射走时曲线对齐后的 semblance 一致性属性。

    公式为 ``(sum_i w_i)^2 / (N * sum_i w_i^2 + eps)``。这里的 ``i`` 是
    对齐后的 shot-channel 窗口，``w_i`` 是去均值并按 RMS 归一化后的局部
    波形。候选点越合理，多个炮和多个通道在对齐后越可能呈现相似波形，
    semblance 越高。
    """

    windows, valid, _ = extract_aligned_windows(data, time_axis, candidate_times, half_width_s)
    windows = windows[valid]
    if windows.shape[0] < 2:
        return 0.0
    centered = windows - np.mean(windows, axis=1, keepdims=True)
    rms = np.sqrt(np.mean(centered * centered, axis=1, keepdims=True))
    usable = rms[:, 0] > EPS
    centered = centered[usable] / np.maximum(rms[usable], EPS)
    if centered.shape[0] < 2:
        return 0.0
    numerator = np.sum(centered, axis=0) ** 2
    denominator = centered.shape[0] * np.sum(centered * centered, axis=0) + EPS
    semblance_by_sample = numerator / denominator
    return float(np.mean(semblance_by_sample))


def spectral_centroid(window: np.ndarray, dt_s: float) -> float:
    """计算局部窗口的谱质心，单位 Hz。

    谱质心用于 frequency_shift_score。若空洞或松散体造成高频衰减，则候选
    窗口相对背景窗口可能表现为谱质心下降。本函数只是最小可用诊断，不是
    严格的 Q 衰减反演。
    """

    if window.size < 3:
        return 0.0
    tapered = (window - np.mean(window)) * np.hanning(window.size)
    spectrum = np.abs(np.fft.rfft(tapered))
    freqs = np.fft.rfftfreq(window.size, d=dt_s)
    power = spectrum * spectrum
    total = float(np.sum(power))
    if total <= EPS:
        return 0.0
    return float(np.sum(freqs * power) / total)


def compute_frequency_shift_score(
    data: np.ndarray,
    time_axis: np.ndarray,
    candidate_times: np.ndarray,
    half_width_s: float,
) -> float:
    """计算最小可用 frequency shift 诊断属性。

    做法
    ----
    1. 在候选绕射走时附近截取局部窗口；
    2. 在同一 shot-channel 上向后偏移两个窗口宽度取背景窗口；
    3. 计算两者谱质心；
    4. 若候选窗口谱质心低于背景窗口，则认为存在高频衰减迹象。

    返回值是 ``max(0, (background_centroid - local_centroid) / background_centroid)``
    的稳健平均。默认权重仍为 0，因此它不会自动支配主定位。
    """

    _, dt = _candidate_center_indices(time_axis, candidate_times)
    local_windows, valid, _ = extract_aligned_windows(data, time_axis, candidate_times, half_width_s)
    background_times = candidate_times + 4.0 * half_width_s
    background_windows, background_valid, _ = extract_aligned_windows(data, time_axis, background_times, half_width_s)
    usable = valid & background_valid
    shifts: list[float] = []
    for local, background, is_usable in zip(local_windows, background_windows, usable):
        if not is_usable:
            continue
        local_centroid = spectral_centroid(local, dt)
        background_centroid = spectral_centroid(background, dt)
        if background_centroid > EPS:
            shifts.append(max(0.0, (background_centroid - local_centroid) / background_centroid))
    if not shifts:
        return 0.0
    return float(np.percentile(np.asarray(shifts, dtype=float), 75.0))


def score_candidate_attributes(
    data: np.ndarray,
    cumulative_energy: np.ndarray,
    trace_energy: np.ndarray,
    time_axis: np.ndarray,
    candidate_times: np.ndarray,
    half_width_s: float,
    frequency_hz: float = 35.0,
    include_frequency_shift: bool = False,
) -> dict[str, float]:
    """计算候选三维点的多属性得分。

    输入 ``data`` 的 shape 必须为 ``shot x time x channel``；
    ``candidate_times`` 的 shape 必须为 ``shot x channel``。所有属性都沿
    同一条理论绕射走时曲线提取，确保 energy、matched wavelet、semblance
    和 frequency shift 比较的是同一个三维候选点。
    """

    center_index, dt = _candidate_center_indices(time_axis, candidate_times)
    half_samples = int(np.ceil(half_width_s / dt))
    energy, valid = _window_energy(cumulative_energy, center_index, half_samples)
    normalized_energy = energy / np.maximum(trace_energy, EPS)
    normalized_energy[~valid] = 0.0

    windows, window_valid, sample_offsets_s = extract_aligned_windows(data, time_axis, candidate_times, half_width_s)
    if np.any(window_valid):
        template = ricker(sample_offsets_s, frequency_hz)
        corr = normalized_correlation_with_template(windows, template, window_valid)
        valid_corr = np.abs(corr[window_valid])
        matched_wavelet = float(np.percentile(valid_corr, 75.0)) if valid_corr.size else 0.0

        semblance_windows = windows[window_valid]
        centered_windows = semblance_windows - np.mean(semblance_windows, axis=1, keepdims=True)
        rms = np.sqrt(np.mean(centered_windows * centered_windows, axis=1, keepdims=True))
        usable = rms[:, 0] > EPS
        if np.count_nonzero(usable) >= 2:
            aligned = centered_windows[usable] / np.maximum(rms[usable], EPS)
            numerator = np.sum(aligned, axis=0) ** 2
            denominator = aligned.shape[0] * np.sum(aligned * aligned, axis=0) + EPS
            semblance = float(np.mean(numerator / denominator))
        else:
            semblance = 0.0
    else:
        matched_wavelet = 0.0
        semblance = 0.0

    frequency_shift = compute_frequency_shift_score(data, time_axis, candidate_times, half_width_s) if include_frequency_shift else 0.0
    return {
        "energy_score": float(np.mean(energy)),
        "normalized_energy_score": float(np.mean(normalized_energy)),
        "matched_wavelet_score": matched_wavelet,
        "semblance_score": semblance,
        "frequency_shift_score": frequency_shift,
    }


def combine_attribute_scores(attribute_scores: dict[str, float], weights: dict[str, float]) -> float:
    """按权重组合候选点属性。

    当前组合发生在候选点级别。各属性体在后续图件和消融实验中会单独输出，
    因此即使组合得分未显著优于 energy stack，也可以审计每个属性的贡献和误导。
    """

    total_weight = sum(value for value in weights.values() if value > 0)
    if total_weight <= 0:
        return attribute_scores["energy_score"]
    return float(sum(attribute_scores[name] * weight for name, weight in weights.items()) / max(total_weight, EPS))
