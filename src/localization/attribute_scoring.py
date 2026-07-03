"""多属性定位评分。"""

from __future__ import annotations

from typing import Any

import numpy as np


EPS = 1.0e-12


def _window_energy(
    cumulative_energy: np.ndarray,
    center_index: np.ndarray,
    half_samples: int,
) -> tuple[np.ndarray, np.ndarray]:
    """用累计能量提取每个 shot-channel 的局部窗口能量。"""

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


def score_candidate_attributes(
    data: np.ndarray,
    cumulative_energy: np.ndarray,
    trace_energy: np.ndarray,
    time_axis: np.ndarray,
    candidate_times: np.ndarray,
    half_width_s: float,
) -> dict[str, float]:
    """计算候选点的多属性得分。

    输入 data shape = shot × time × channel。candidate_times shape = shot × channel。

    属性：
        energy_score：候选绕射走时时间窗局部能量均值；
        normalized_energy_score：局部能量除以每道总能量后求均值；
        matched_wavelet_score：中心样值相对窗口能量的快速归一化匹配近似；
        semblance_score：中心样值在多炮多道上的一致性；
        frequency_shift_score：本轮预留，返回 0。

    限制：
        matched_wavelet_score 是 Stage 4A 的轻量近似，不是完整滑动子波匹配滤波。
        这样做是为了让默认 full_pipeline 保持本地快速可跑。
    """

    dt = float(time_axis[1] - time_axis[0]) if len(time_axis) > 1 else 1.0
    half_samples = int(np.ceil(half_width_s / dt))
    center_index = np.rint((candidate_times - time_axis[0]) / dt).astype(int)
    energy, valid = _window_energy(cumulative_energy, center_index, half_samples)
    normalized_energy = energy / np.maximum(trace_energy, EPS)

    n_shot, n_time, n_channel = data.shape
    clipped_center = np.clip(center_index, 0, n_time - 1)
    shot_index = np.arange(n_shot)[:, None]
    channel_index = np.arange(n_channel)[None, :]
    center_samples = data[shot_index, clipped_center, channel_index]
    center_samples[~valid] = 0.0
    matched = np.abs(center_samples) / np.sqrt(np.maximum(energy, EPS))
    samples = center_samples.ravel()
    semblance = float((np.sum(samples) ** 2) / (len(samples) * np.sum(samples * samples) + EPS))
    return {
        "energy_score": float(np.mean(energy)),
        "normalized_energy_score": float(np.mean(normalized_energy)),
        "matched_wavelet_score": float(np.mean(matched)),
        "semblance_score": semblance,
        "frequency_shift_score": 0.0,
    }


def combine_attribute_scores(attribute_scores: dict[str, float], weights: dict[str, float]) -> float:
    """按权重组合属性得分。

    当前为候选点级别的加权和。score volume 完成后还会做全局归一化用于绘图和报告。
    """

    total_weight = sum(value for value in weights.values() if value > 0)
    if total_weight <= 0:
        return attribute_scores["energy_score"]
    return float(
        sum(attribute_scores[name] * weight for name, weight in weights.items()) / max(total_weight, EPS)
    )

