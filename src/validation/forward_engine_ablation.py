"""正演引擎消融验证。

Stage 5B 的目的不是简单增加一个新开关，而是把 forward modeling 单独作为可审计
主线：F0 均匀运动学基线、F1 分层/非均匀 straight-ray 运动学主线、F2 acoustic2d
波动方程基础设施验证。这里的 acoustic2d 只验证数值框架，不参与 DAS-like 主定位。
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from src.forward.acoustic2d.acoustic_fdtd import Acoustic2DResult, run_acoustic2d_prototype
from src.forward.forward_registry import get_forward_engine_spec, list_forward_engines
from src.forward.kinematic_baseline import run_kinematic_baseline_forward
from src.forward.layered_kinematic import run_layered_kinematic_forward
from src.localization.travel_time import compute_candidate_diffraction_times
from src.validation.common import clone_params


ROADMAP_STATUS = [
    {
        "stage": "F0",
        "name": "kinematic_baseline",
        "status": "implemented_baseline",
        "role": "快速均匀速度运动学基线，不是当前主正演。",
    },
    {
        "stage": "F1",
        "name": "layered_kinematic",
        "status": "active_forward",
        "role": "当前主流程：分层/非均匀 straight-ray kinematic approximation。",
    },
    {
        "stage": "F2",
        "name": "acoustic2d_prototype",
        "status": "implemented_validation",
        "role": "声学波动方程基础设施验证，不代表 Rayleigh 波。",
    },
    {
        "stage": "F3",
        "name": "elastic2d",
        "status": "designed_next",
        "role": "下一步 Rayleigh/free-surface/void scattering 局部全波场方向。",
    },
    {
        "stage": "F4",
        "name": "multi_section_elastic",
        "status": "planned",
        "role": "面向三维几何的多剖面 elastic validation。",
    },
    {
        "stage": "F5",
        "name": "local_3d_elastic",
        "status": "long_term",
        "role": "小域局部 3D elastic validation，不是默认主流程。",
    },
    {
        "stage": "F6",
        "name": "external_solver_adapters",
        "status": "planned_adapters",
        "role": "Devito/Deepwave/SPECFEM/k-Wave 等 adapter 计划，不复制第三方代码。",
    },
]


def _rms(data: np.ndarray) -> float:
    """计算 RMS，避免各处重复写平方均值。"""

    return float(np.sqrt(np.mean(np.asarray(data, dtype=float) ** 2)))


def _summarize_kinematic_result(result: dict[str, Any]) -> dict[str, Any]:
    """提取运动学正演结果摘要。

    只把可 JSON 化的轻量指标写入报告和 metadata；完整数组仍留在运行目录或内存中，
    避免 latest_stable summary 变得不可审计。
    """

    velocity_model = result["velocity_model"]
    return {
        "forward_engine": result.get("forward_engine"),
        "forward_stage": result.get("forward_stage"),
        "velocity_model_type": getattr(velocity_model, "model_type", "unknown"),
        "representative_velocity_mps": float(velocity_model.get_velocity()),
        "data_shape": tuple(int(v) for v in result["synthetic_data"].shape),
        "direct_rms": _rms(result["direct_data"]),
        "scatter_rms": _rms(result["scatter_data"]),
        "synthetic_rms": _rms(result["synthetic_data"]),
    }


def _summarize_acoustic_result(result: Acoustic2DResult) -> dict[str, Any]:
    """提取 acoustic2d prototype 的轻量摘要。"""

    return {
        "forward_engine": "acoustic2d_prototype",
        "forward_stage": "F2",
        "shot_gather_shape": tuple(int(v) for v in result.shot_gather.shape),
        "wavefield_snapshot_shape": tuple(int(v) for v in result.wavefield_snapshots.shape),
        "snapshot_count": int(result.wavefield_snapshots.shape[0]),
        "cfl_stable": bool(result.cfl_info["stable"]),
        "cfl_number": float(result.cfl_info["cfl_number"]),
        "max_abs_amplitude": float(result.diagnostics["max_abs_amplitude"]),
        "energy": float(result.diagnostics["energy"]),
        "limitation": "2D scalar acoustic FDTD 只验证波动方程框架，不能代表 Rayleigh/free-surface/void scattering。",
    }


def run_forward_engine_ablation(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
) -> dict[str, Any]:
    """运行正演引擎轻量消融。

    F0 和 F1 使用完全相同的三维 source/receiver/scatter 几何，差别只在 velocity_model。
    acoustic2d 使用小型二维标量声学网格做 validation prototype，不把它的炮集输入
    后续 DAS-like 定位流程。
    """

    baseline_params = clone_params(params)
    baseline_params.forward.engine = "kinematic_baseline"
    layered_params = clone_params(params)
    layered_params.forward.engine = "layered_kinematic"

    baseline = run_kinematic_baseline_forward(
        baseline_params,
        source_xyz,
        receiver_xyz,
        scatter_xyz,
        scatter_weight,
    )
    layered = run_layered_kinematic_forward(
        layered_params,
        source_xyz,
        receiver_xyz,
        scatter_xyz,
        scatter_weight,
    )

    truth_xyz = np.array([params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m], dtype=float)
    baseline_times = compute_candidate_diffraction_times(
        truth_xyz,
        source_xyz,
        receiver_xyz,
        baseline["velocity_model"],
        t0_s=params.time.t0_s,
    )
    layered_times = compute_candidate_diffraction_times(
        truth_xyz,
        source_xyz,
        receiver_xyz,
        layered["velocity_model"],
        t0_s=params.time.t0_s,
    )
    time_residual = layered_times - baseline_times
    gather_difference = layered["synthetic_data"] - baseline["synthetic_data"]
    baseline_rms = _rms(baseline["synthetic_data"])

    # acoustic2d prototype 始终在 forward ablation 中跑一次，保证 latest_stable 有
    # 波动方程基础设施验证图。它不改变 params.forward.engine，也不参与主定位。
    acoustic_result = run_acoustic2d_prototype(params)
    acoustic_summary = _summarize_acoustic_result(acoustic_result)

    return {
        "available_forward_engines": list_forward_engines(),
        "active_forward_engine": params.forward.engine,
        "default_localization_forward": "layered_kinematic",
        "next_required_forward": "elastic2d",
        "roadmap_status": ROADMAP_STATUS,
        "engines": {
            "kinematic_baseline": _summarize_kinematic_result(baseline),
            "layered_kinematic": _summarize_kinematic_result(layered),
            "acoustic2d_prototype": acoustic_summary,
        },
        "layered_vs_baseline": {
            "synthetic_rms_difference": _rms(gather_difference),
            "synthetic_relative_difference": _rms(gather_difference) / max(baseline_rms, 1.0e-12),
            "travel_time_residual_mean_ms": float(np.mean(time_residual) * 1000.0),
            "travel_time_residual_rms_ms": float(np.sqrt(np.mean(time_residual**2)) * 1000.0),
            "travel_time_residual_max_abs_ms": float(np.max(np.abs(time_residual)) * 1000.0),
            "direct_wave_uses_velocity_model_interface": True,
            "scatter_wave_uses_velocity_model_interface": True,
            "scan_uses_velocity_model_interface": True,
        },
        "baseline_synthetic_data": baseline["synthetic_data"],
        "layered_synthetic_data": layered["synthetic_data"],
        "acoustic2d_result": acoustic_result,
        "forward_specs": {
            name: {
                "stage": get_forward_engine_spec(name).stage,
                "description": get_forward_engine_spec(name).description,
                "limitation": get_forward_engine_spec(name).limitation,
                "is_default_localization_forward": get_forward_engine_spec(name).is_default_localization_forward,
            }
            for name in list_forward_engines()
        },
        "note": (
            "layered_kinematic 是当前主定位 forward；kinematic_baseline 只作基线；"
            "acoustic2d_prototype 只验证声学波动方程基础设施，不能代表 Rayleigh 波。"
        ),
    }


def strip_forward_engine_ablation_arrays(result: dict[str, Any] | None) -> dict[str, Any] | None:
    """删除大数组，得到可写入 metadata/summary 的 Stage 5B 摘要。"""

    if result is None:
        return None
    return {
        key: value
        for key, value in result.items()
        if key not in {"baseline_synthetic_data", "layered_synthetic_data", "acoustic2d_result"}
    }
