"""速度模型主线审计。

Stage 5D 的目标之一，是证明速度模型不是“文件存在但主流程没用”。本模块通过
参数、实际 velocity_model 对象、源码调用链和示例走时差异一起检查：
direct、scatter、scan 是否都经过 velocity_model travel-time 接口，当前默认是否
仍为 layered，以及 uniform 是否只作为 baseline/诊断存在。
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np

from src.model.velocity_model import (
    UniformVelocityModel,
    build_velocity_model,
    compute_kinematic_travel_time,
    compute_scatter_travel_time,
)


def _file_contains(path: Path, text: str) -> bool:
    """读取源码并检查关键调用。文件缺失时返回 False。"""

    if not path.exists():
        return False
    return text in path.read_text(encoding="utf-8")


def _path_travel_time_examples(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
) -> dict[str, Any]:
    """构造 uniform/layered 的示例走时差异。

    这里不是重新做扫描，而是选取少量 source-scatter-receiver 路径，直接调用
    travel-time 接口，证明 layered 模型会改变走时。
    """

    active_model = build_velocity_model(params)
    uniform_model = UniformVelocityModel(params.velocity.rayleigh_velocity_mps)
    source = np.asarray(source_xyz[: min(3, len(source_xyz))], dtype=float)
    receiver = np.asarray(receiver_xyz[:: max(1, len(receiver_xyz) // 6)], dtype=float)
    scatter = np.asarray(scatter_xyz[:1], dtype=float)
    active_direct = compute_kinematic_travel_time(source[:, None, :], receiver[None, :, :], active_model)
    uniform_direct = compute_kinematic_travel_time(source[:, None, :], receiver[None, :, :], uniform_model)
    active_scatter = compute_scatter_travel_time(source, scatter, receiver, active_model)[:, 0, :]
    uniform_scatter = compute_scatter_travel_time(source, scatter, receiver, uniform_model)[:, 0, :]
    direct_diff_ms = 1000.0 * (active_direct - uniform_direct)
    scatter_diff_ms = 1000.0 * (active_scatter - uniform_scatter)
    return {
        "direct_diff_mean_ms": float(np.mean(direct_diff_ms)),
        "direct_diff_rms_ms": float(np.sqrt(np.mean(direct_diff_ms**2))),
        "direct_diff_max_abs_ms": float(np.max(np.abs(direct_diff_ms))),
        "scatter_diff_mean_ms": float(np.mean(scatter_diff_ms)),
        "scatter_diff_rms_ms": float(np.sqrt(np.mean(scatter_diff_ms**2))),
        "scatter_diff_max_abs_ms": float(np.max(np.abs(scatter_diff_ms))),
        "active_direct_times_s": active_direct,
        "uniform_direct_times_s": uniform_direct,
        "active_scatter_times_s": active_scatter,
        "uniform_scatter_times_s": uniform_scatter,
    }


def run_velocity_model_audit(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """执行速度模型主线审计。"""

    repo_root = Path.cwd() if repo_root is None else Path(repo_root)
    active_model = build_velocity_model(params)
    source_checks = {
        "direct_wave_uses_compute_kinematic_travel_time": _file_contains(
            repo_root / "src" / "forward" / "direct_wave.py",
            "compute_kinematic_travel_time",
        ),
        "scatter_wave_uses_compute_scatter_travel_time": _file_contains(
            repo_root / "src" / "forward" / "scatter_kinematic.py",
            "compute_scatter_travel_time",
        ),
        "scan_uses_compute_scatter_travel_time": _file_contains(
            repo_root / "src" / "localization" / "travel_time.py",
            "compute_scatter_travel_time",
        ),
        "forward_pipeline_builds_velocity_model": _file_contains(
            repo_root / "src" / "pipeline" / "run_forward_pipeline.py",
            "velocity_model",
        ),
    }
    examples = _path_travel_time_examples(params, source_xyz, receiver_xyz, scatter_xyz)
    representative_velocity_calls = []
    for rel in [
        "src/forward/kinematic_baseline.py",
        "src/model/velocity_model.py",
        "src/pipeline/run_forward_pipeline.py",
    ]:
        text = (repo_root / rel).read_text(encoding="utf-8")
        if "get_velocity" in text or "rayleigh_velocity_mps" in text:
            representative_velocity_calls.append(rel)
    direct_ok = source_checks["direct_wave_uses_compute_kinematic_travel_time"]
    scatter_ok = source_checks["scatter_wave_uses_compute_scatter_travel_time"]
    scan_ok = source_checks["scan_uses_compute_scatter_travel_time"]
    return {
        "active_velocity_model_type": getattr(active_model, "model_type", params.velocity.model_type),
        "argparse_default_velocity_model_type": params.velocity.model_type,
        "active_velocity_model_confirmed": getattr(active_model, "model_type", None) == params.velocity.model_type,
        "is_layered_default": params.velocity.model_type == "layered",
        "layer_depths_m": list(params.velocity.layer_depths_m),
        "layer_rayleigh_velocities_mps": list(params.velocity.layer_rayleigh_velocities_mps),
        "direct_uses_velocity_model_travel_time": direct_ok,
        "scatter_uses_velocity_model_travel_time": scatter_ok,
        "scan_uses_velocity_model_travel_time": scan_ok,
        "velocity_model_used_by_direct": direct_ok,
        "velocity_model_used_by_scatter": scatter_ok,
        "velocity_model_used_by_scan": scan_ok,
        "source_checks": source_checks,
        "representative_velocity_call_sites": representative_velocity_calls,
        "uniform_only_baseline": "src/forward/kinematic_baseline.py" in representative_velocity_calls,
        "travel_time_difference": {
            key: value for key, value in examples.items() if not isinstance(value, np.ndarray)
        },
        "elastic2d_velocity_note": (
            "elastic2d_prototype 使用独立 Vp/Vs/rho 弹性参数；它与 layered_kinematic 的 "
            "Rayleigh equivalent velocity model 不是同一套物理参数。"
        ),
        "status": "pass" if params.velocity.model_type == "layered" and direct_ok and scatter_ok and scan_ok else "fail",
    }


def write_velocity_model_audit_report(path: Path, result: dict[str, Any]) -> None:
    """写出速度模型审计报告。"""

    lines = [
        "# 速度模型主线审计报告",
        "",
        "本报告检查 layered / heterogeneous 等效 Rayleigh 速度模型是否真正进入主流程，",
        "而不是只停留在 `src/model/` 文件中。",
        "",
        f"- 当前 active velocity_model_type：`{result['active_velocity_model_type']}`",
        f"- argparse / full_pipeline velocity_model_type：`{result['argparse_default_velocity_model_type']}`",
        f"- 是否确认为 layered：`{result['is_layered_default']}`",
        f"- direct wave 使用 travel-time 接口：`{result['direct_uses_velocity_model_travel_time']}`",
        f"- scatter wave 使用 travel-time 接口：`{result['scatter_uses_velocity_model_travel_time']}`",
        f"- scan candidate 使用 travel-time 接口：`{result['scan_uses_velocity_model_travel_time']}`",
        f"- layer depths m：`{result['layer_depths_m']}`",
        f"- layer velocities m/s：`{result['layer_rayleigh_velocities_mps']}`",
        "",
        "## representative velocity 调用点",
        "",
    ]
    for item in result["representative_velocity_call_sites"]:
        if item == "src/forward/kinematic_baseline.py":
            lines.append(f"- `{item}`：合法 baseline 使用。")
        else:
            lines.append(f"- `{item}`：诊断/metadata/兼容用途，需要继续人工关注。")
    diff = result["travel_time_difference"]
    lines.extend(
        [
            "",
            "## uniform 与 active model 走时差异",
            "",
            f"- direct RMS 差异：`{diff['direct_diff_rms_ms']:.4g}` ms",
            f"- direct 最大绝对差异：`{diff['direct_diff_max_abs_ms']:.4g}` ms",
            f"- scatter RMS 差异：`{diff['scatter_diff_rms_ms']:.4g}` ms",
            f"- scatter 最大绝对差异：`{diff['scatter_diff_max_abs_ms']:.4g}` ms",
            "",
            "## elastic2d 说明",
            "",
            result["elastic2d_velocity_note"],
            "",
            "当前结果仍是 straight-ray kinematic approximation 与 validation prototype，不能写成工程确诊。",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
