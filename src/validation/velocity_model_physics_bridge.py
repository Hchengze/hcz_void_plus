"""Rayleigh equivalent velocity 与 elastic Vp/Vs/rho 的物理关系桥接。

Stage 5D 已确认主流程使用 layered equivalent Rayleigh velocity，但 elastic2d 使用
独立 Vp/Vs/rho。二者不是同一模型。本模块用简单经验关系 Vr≈0.9Vs 做一致性
诊断，帮助判断 Rayleigh-like 检测失败是否可能与参数层级不匹配有关。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


def run_velocity_model_physics_bridge(params) -> dict[str, Any]:
    """计算 layered Rayleigh velocity 与 elastic2d 参数的关系。"""

    rayleigh_velocity = np.asarray(params.velocity.layer_rayleigh_velocities_mps, dtype=float)
    layer_depths = np.asarray(params.velocity.layer_depths_m, dtype=float)
    implied_vs = rayleigh_velocity / 0.9
    elastic_vs = float(params.forward.elastic2d_vs_mps)
    elastic_vp = float(params.forward.elastic2d_vp_mps)
    elastic_rho = float(params.forward.elastic2d_rho_kgm3)
    elastic_rayleigh_equivalent = 0.9 * elastic_vs
    mismatch = rayleigh_velocity - elastic_rayleigh_equivalent
    relative_mismatch = mismatch / np.maximum(rayleigh_velocity, 1.0e-9)
    representative_rayleigh = float(np.median(rayleigh_velocity))
    representative_implied_vs = representative_rayleigh / 0.9
    consistency_ratio = elastic_vs / max(representative_implied_vs, 1.0e-9)
    consistent = bool(0.8 <= consistency_ratio <= 1.25)
    return {
        "layer_depths_m": layer_depths.tolist(),
        "layer_rayleigh_equivalent_velocity_mps": rayleigh_velocity.tolist(),
        "implied_vs_from_rayleigh_mps": implied_vs.tolist(),
        "empirical_relation": "Rayleigh equivalent velocity ≈ 0.9 * Vs",
        "elastic2d_vp_mps": elastic_vp,
        "elastic2d_vs_mps": elastic_vs,
        "elastic2d_rho_kgm3": elastic_rho,
        "elastic2d_rayleigh_equivalent_mps": elastic_rayleigh_equivalent,
        "velocity_mismatch_mps": mismatch.tolist(),
        "relative_mismatch": relative_mismatch.tolist(),
        "representative_rayleigh_mps": representative_rayleigh,
        "representative_implied_vs_mps": representative_implied_vs,
        "elastic_vs_to_implied_vs_ratio": consistency_ratio,
        "rayleigh_equivalent_vs_elastic_consistency": "consistent" if consistent else "mismatch",
        "rayleigh_pick_failure_may_reflect_parameter_mismatch": not consistent,
        "status": "generated",
        "note": (
            "layered_kinematic 的速度是 Rayleigh equivalent velocity；elastic2d 的 Vp/Vs/rho "
            "是弹性介质参数。二者必须通过经验关系或实测标定建立联系。"
        ),
    }


def write_velocity_model_physics_bridge_report(path: Path, result: dict[str, Any]) -> None:
    """写出速度模型物理桥接报告。"""

    lines = [
        "# 速度模型物理关系桥接报告",
        "",
        "本报告澄清 layered_kinematic 与 elastic2d 使用的是不同层级的速度模型。",
        "",
        f"- empirical relation：`{result['empirical_relation']}`",
        f"- layered Rayleigh equivalent velocity：`{result['layer_rayleigh_equivalent_velocity_mps']}` m/s",
        f"- implied Vs from Rayleigh：`{result['implied_vs_from_rayleigh_mps']}` m/s",
        f"- elastic2d Vp：`{result['elastic2d_vp_mps']}` m/s",
        f"- elastic2d Vs：`{result['elastic2d_vs_mps']}` m/s",
        f"- elastic2d rho：`{result['elastic2d_rho_kgm3']}` kg/m3",
        f"- elastic2d 0.9Vs equivalent：`{result['elastic2d_rayleigh_equivalent_mps']}` m/s",
        f"- consistency：`{result['rayleigh_equivalent_vs_elastic_consistency']}`",
        f"- elastic Vs / implied Vs ratio：`{result['elastic_vs_to_implied_vs_ratio']:.4g}`",
        f"- Rayleigh pick failure may reflect parameter mismatch：`{result['rayleigh_pick_failure_may_reflect_parameter_mismatch']}`",
        "",
        "## 结论",
        "",
        "当前 elastic2d 参数不能自动代表主流程的 layered Rayleigh equivalent velocity。",
        "如果二者不匹配，Rayleigh-like 拾取失败可能同时包含数值格式问题和参数物理层级不一致问题。",
        "下一步应从 Rayleigh equivalent velocity 反推 Vs，并用实测或文献关系约束 Vp/Vs/rho。",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
