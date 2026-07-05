"""路径相关经验衰减模型。

Stage 5J 只引入轻量 Q attenuation，用来修正 layered_kinematic 正演中过于理想化的振幅。
它不是粘弹性波动方程，也不改变走时；所有走时仍来自 velocity_model 的三维路径积分接口。
"""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import numpy as np


@dataclass(frozen=True)
class AttenuationModel:
    """经验衰减参数容器。

    参数含义：
    enabled：是否启用 Q attenuation。
    q_default：没有分层 Q 可用时的默认 Q。
    layer_depths_m / layer_q：按深度向下为正的分层 Q 描述。
    frequency_dependent：是否使用 exp(-pi*f*t/Q) 频率相关衰减。
    geometric_spreading_power：几何扩散指数 p，对应 1/(path+1)^p。
    min_amplitude：数值下限，避免极远路径完全下溢。
    """

    enabled: bool
    q_default: float
    layer_depths_m: np.ndarray
    layer_q: np.ndarray
    frequency_dependent: bool
    geometric_spreading_power: float
    min_amplitude: float

    def q_at_depth(self, depth_m: np.ndarray | float) -> np.ndarray:
        """返回给定深度处的 Q 值，深度 h 向下为正。"""

        depth = np.asarray(depth_m, dtype=float)
        if self.layer_q.size == 0:
            return np.full_like(depth, self.q_default, dtype=float)
        indices = np.searchsorted(self.layer_depths_m, depth, side="right")
        indices = np.clip(indices, 0, self.layer_q.size - 1)
        return np.maximum(self.layer_q[indices], 1.0e-6)

    def effective_q_for_path(self, start_xyz: np.ndarray, end_xyz: np.ndarray, n_samples: int = 16) -> np.ndarray:
        """沿直线路径采样 Q，并用调和平均得到路径等效 Q。

        Q 是经验振幅项，不参与走时积分；这里的采样只用于让深部路径和浅部路径有不同衰减。
        """

        start = np.asarray(start_xyz, dtype=float)
        end = np.asarray(end_xyz, dtype=float)
        start_b, end_b = np.broadcast_arrays(start, end)
        fractions = np.linspace(0.0, 1.0, max(2, int(n_samples)), dtype=float)
        fraction_shape = (1,) * (start_b.ndim - 1) + (len(fractions), 1)
        samples = start_b[..., None, :] + fractions.reshape(fraction_shape) * (end_b - start_b)[..., None, :]
        q_values = self.q_at_depth(samples[..., 2])
        return 1.0 / np.mean(1.0 / np.maximum(q_values, 1.0e-6), axis=-1)

    def q_decay(self, travel_time_s: np.ndarray | float, dominant_frequency_hz: float, q_eff: np.ndarray | float) -> np.ndarray:
        """计算 Q 衰减项 exp(-pi*f*t/Q)。"""

        time = np.asarray(travel_time_s, dtype=float)
        if not self.enabled or not self.frequency_dependent:
            return np.ones_like(time, dtype=float)
        decay = np.exp(-np.pi * float(dominant_frequency_hz) * np.maximum(time, 0.0) / np.maximum(q_eff, 1.0e-6))
        return np.maximum(decay, self.min_amplitude)


def build_attenuation_model(params: SimpleNamespace) -> AttenuationModel:
    """从 main.py 的统一参数构建衰减模型。"""

    layer_q = np.asarray(params.attenuation.layer_q, dtype=float)
    layer_depths = np.asarray(params.velocity.layer_depths_m, dtype=float)
    if layer_q.size == 0:
        layer_q = np.asarray([params.attenuation.q_default], dtype=float)
    if layer_depths.size != layer_q.size:
        # 分层 Q 与速度层数量不一致时，按最后一个 Q 补齐或截断。这样命令行仍保持宽容，
        # 但 metadata 会记录实际使用的 layer_q。
        if layer_q.size < layer_depths.size:
            pad = np.full(layer_depths.size - layer_q.size, layer_q[-1], dtype=float)
            layer_q = np.concatenate([layer_q, pad])
        else:
            layer_q = layer_q[: layer_depths.size]
    return AttenuationModel(
        enabled=bool(params.attenuation.enabled),
        q_default=float(params.attenuation.q_default),
        layer_depths_m=layer_depths,
        layer_q=np.maximum(layer_q, 1.0e-6),
        frequency_dependent=bool(params.attenuation.frequency_dependent),
        geometric_spreading_power=float(params.attenuation.geometric_spreading_power),
        min_amplitude=float(params.attenuation.min_amplitude),
    )


def attenuation_metadata(model: AttenuationModel) -> dict[str, object]:
    """生成可写入 meta_run.json 的衰减参数摘要。"""

    return {
        "attenuation_enabled": model.enabled,
        "q_default": model.q_default,
        "layer_q": model.layer_q.tolist(),
        "frequency_dependent": model.frequency_dependent,
        "geometric_spreading_power": model.geometric_spreading_power,
        "min_amplitude": model.min_amplitude,
        "attenuation_note": "empirical Q attenuation, not viscoelastic wave equation",
    }
