"""速度模型定义。"""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace


@dataclass(frozen=True)
class UniformVelocityModel:
    """均匀等效瑞雷波速度模型。

    物理意义：
        用一个统一的 effective Rayleigh velocity 表示道路浅层介质中的主要
        运动学传播速度。

    输入参数单位：
        rayleigh_velocity_mps：m/s。

    输出：
        get_velocity() 返回 m/s。

    近似条件和限制：
        当前不是分层速度模型，也不包含频散、各向异性或局部低速体；metadata
        会诚实说明这是 uniform effective Rayleigh velocity。
    """

    rayleigh_velocity_mps: float
    model_type: str = "uniform"

    def get_velocity(self) -> float:
        """返回当前等效瑞雷波速度，单位 m/s。"""

        return self.rayleigh_velocity_mps


def build_velocity_model(params: SimpleNamespace) -> UniformVelocityModel:
    """从统一 params 构建速度模型。"""

    return UniformVelocityModel(
        rayleigh_velocity_mps=params.velocity.rayleigh_velocity_mps,
        model_type=params.velocity.model_type,
    )
