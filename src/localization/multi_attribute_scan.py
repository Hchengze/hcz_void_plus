"""多属性扫描结果辅助函数。"""

from __future__ import annotations

from types import SimpleNamespace


def score_weights_from_params(params: SimpleNamespace) -> dict[str, float]:
    """从统一 params 读取多属性 score 权重。"""

    return {
        "energy_score": params.scan.weight_energy,
        "normalized_energy_score": params.scan.weight_normalized_energy,
        "matched_wavelet_score": params.scan.weight_matched_wavelet,
        "semblance_score": params.scan.weight_semblance,
        "frequency_shift_score": params.scan.weight_frequency_shift,
    }

