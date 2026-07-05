"""多属性三维扫描结果辅助函数。

Stage 5I 开始把 energy、matched wavelet、semblance、frequency shift 等属性真正形成
三维体，再做稳健归一化和加权合成。这样 combined score 不再是某个候选点局部量纲的
简单平均，而是可保存、可审计、可用于 posterior-like 诊断的三维反演输入。
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np


def score_weights_from_params(params: SimpleNamespace) -> dict[str, float]:
    """从统一 params 读取多属性 score 权重。"""

    return {
        "energy_score": params.scan.weight_energy,
        "normalized_energy_score": params.scan.weight_normalized_energy,
        "matched_wavelet_score": params.scan.weight_matched_wavelet,
        "semblance_score": params.scan.weight_semblance,
        "frequency_shift_score": params.scan.weight_frequency_shift,
    }


def normalize_attribute_volume(volume: np.ndarray, method: str = "robust_minmax") -> np.ndarray:
    """对单个属性体做稳健归一化。

    ``robust_minmax`` 使用 2% 和 98% 分位数，适合压制少数极端高能量点；
    ``zscore_percentile`` 先做稳健 z-score，再把 -3 到 +3 映射到 0-1。
    两者都只改变属性体量纲，不改变 candidate_xyz 网格结构。
    """

    arr = np.asarray(volume, dtype=float)
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return np.zeros_like(arr, dtype=float)
    if method == "zscore_percentile":
        center = float(np.percentile(finite, 50.0))
        spread = float(np.percentile(finite, 84.0) - np.percentile(finite, 16.0))
        if spread <= 1.0e-12:
            return np.zeros_like(arr, dtype=float)
        z = np.clip((arr - center) / spread, -3.0, 3.0)
        return (z + 3.0) / 6.0

    low = float(np.percentile(finite, 2.0))
    high = float(np.percentile(finite, 98.0))
    if high <= low:
        return np.zeros_like(arr, dtype=float)
    return np.clip((arr - low) / (high - low), 0.0, 1.0)


def build_multi_attribute_score_volumes(
    attribute_volumes: dict[str, np.ndarray],
    weights: dict[str, float],
    normalization: str = "robust_minmax",
) -> dict[str, Any]:
    """从原始属性体生成归一化属性体和 combined score volume。

    返回字段名同时保留内部属性名和 Stage 5I 要求的输出名，方便 pipeline 直接保存：
    ``score_volume_energy``、``score_volume_normalized_energy``、``score_volume_matched_wavelet``、
    ``score_volume_semblance``、``score_volume_frequency_shift`` 和 ``score_volume_combined``。
    """

    normalized: dict[str, np.ndarray] = {}
    combined = None
    total_weight = 0.0
    for name, volume in attribute_volumes.items():
        normalized_volume = normalize_attribute_volume(volume, method=normalization)
        normalized[name] = normalized_volume
        weight = float(weights.get(name, 0.0))
        if weight <= 0:
            continue
        combined = normalized_volume * weight if combined is None else combined + normalized_volume * weight
        total_weight += weight
    if combined is None or total_weight <= 0:
        combined = normalized.get("energy_score", next(iter(normalized.values()))) if normalized else np.zeros(0)
    else:
        combined = combined / total_weight

    return {
        "normalized_attribute_volumes": normalized,
        "score_volume_energy": attribute_volumes.get("energy_score"),
        "score_volume_normalized_energy": attribute_volumes.get("normalized_energy_score"),
        "score_volume_matched_wavelet": attribute_volumes.get("matched_wavelet_score"),
        "score_volume_semblance": attribute_volumes.get("semblance_score"),
        "score_volume_frequency_shift": attribute_volumes.get("frequency_shift_score"),
        "score_volume_combined": combined,
        "attribute_normalization": normalization,
        "attribute_weights": dict(weights),
    }
