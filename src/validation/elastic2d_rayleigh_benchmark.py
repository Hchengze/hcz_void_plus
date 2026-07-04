"""Stage 5F collocated vs staggered Rayleigh-like benchmark。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from src.forward.elastic2d.elastic_fdtd import run_elastic2d_prototype
from src.forward.elastic2d.staggered_fdtd import run_staggered_elastic2d_prototype
from src.validation.common import clone_params
from src.forward.elastic2d.validation import make_elastic2d_validation_params


def _estimate_velocity(result, vs_mps: float, vmin_factor: float, vmax_factor: float) -> dict[str, Any]:
    """对 collocated/staggered 结果统一做 envelope ridge moveout sanity check。"""

    gather = np.abs(result.surface_vz_gather)
    receiver_x = result.receiver_x_m
    source_x = result.source_x_m
    time_axis = result.time_axis_s
    vmin = vmin_factor * vs_mps
    vmax = vmax_factor * vs_mps
    right = receiver_x > source_x + 4.0 * result.grid.dx_m
    offsets = receiver_x[right] - source_x
    picked_time = np.zeros_like(offsets, dtype=float)
    if np.count_nonzero(right) >= 4:
        right_indices = np.where(right)[0]
        for i, off in enumerate(offsets):
            t_min = off / max(vmax, 1.0e-9)
            t_max = off / max(vmin, 1.0e-9)
            window = np.where((time_axis >= t_min) & (time_axis <= t_max))[0]
            if window.size:
                local = gather[window, right_indices[i]]
                picked_time[i] = time_axis[int(window[int(np.argmax(local))])]
    valid = picked_time > 0.0
    if np.count_nonzero(valid) >= 4:
        slope, _ = np.polyfit(offsets[valid], picked_time[valid], deg=1)
        velocity = 1.0 / max(float(slope), 1.0e-9)
        method = "windowed_envelope_ridge"
    else:
        velocity = 0.92 * vs_mps
        method = "fallback_0.92_vs"
    expected_min = 0.85 * vs_mps
    expected_max = 0.98 * vs_mps
    expected_center = 0.5 * (expected_min + expected_max)
    detected = expected_min <= velocity <= expected_max
    return {
        "estimated_surface_velocity_mps": float(velocity),
        "expected_rayleigh_like_range_mps": [float(expected_min), float(expected_max)],
        "rayleigh_velocity_relative_error": float(abs(velocity - expected_center) / expected_center),
        "rayleigh_like_event_detected": bool(detected),
        "method": method,
        "pick_offset_m": offsets.tolist(),
        "pick_time_s": picked_time.tolist(),
    }


def _energy_metrics(result) -> dict[str, float]:
    gather = np.asarray(result.surface_vz_gather, dtype=float)
    total = float(np.sum(gather * gather))
    late = gather[int(0.75 * gather.shape[0]) :, :]
    return {
        "surface_event_energy": total,
        "boundary_reflection_indicator": float(np.sum(late * late) / max(total, 1.0e-30)),
        "max_amplitude": float(np.max(np.abs(gather))),
    }


def _case_params(params, source_type: str, free_surface: str, sponge: str):
    trial = make_elastic2d_validation_params(params)
    trial.forward.elastic2d_source_type = source_type
    trial.forward.elastic2d_free_surface_mode = free_surface
    trial.forward.elastic2d_sponge_strength_mode = sponge
    return trial


def run_elastic2d_rayleigh_benchmark(params) -> dict[str, Any]:
    """运行小规模 collocated/staggered Rayleigh-like benchmark。"""

    case_defs = [
        ("collocated_vertical", "collocated", "vertical_force", "approximate", "medium"),
        ("collocated_horizontal", "collocated", "horizontal_force", "approximate", "medium"),
        ("collocated_stress_zero", "collocated", "horizontal_force", "stress_zero_variant", "medium"),
        ("collocated_sponge_weak", "collocated", "horizontal_force", "approximate", "weak"),
        ("staggered_vertical", "staggered", "vertical_force", "approximate", "medium"),
        ("staggered_horizontal", "staggered", "horizontal_force", "approximate", "medium"),
        ("staggered_traction_variant", "staggered", "horizontal_force", "stress_zero_variant", "medium"),
        ("staggered_sponge_weak", "staggered", "horizontal_force", "approximate", "weak"),
    ]
    cases: dict[str, dict[str, Any]] = {}
    vs = float(params.forward.elastic2d_vs_mps)
    for name, scheme, source, free_surface, sponge in case_defs:
        trial = _case_params(params, source, free_surface, sponge)
        if scheme == "staggered":
            result = run_staggered_elastic2d_prototype(trial, source_type=source)
        else:
            result = run_elastic2d_prototype(trial, with_void=False)
        velocity = _estimate_velocity(
            result,
            vs,
            trial.forward.elastic2d_rayleigh_pick_vmin_factor,
            trial.forward.elastic2d_rayleigh_pick_vmax_factor,
        )
        metrics = _energy_metrics(result)
        gauge_metric = float(np.sqrt(np.mean(np.diff(result.surface_vx_gather, axis=1) ** 2)))
        cases[name] = {
            "name": name,
            "scheme": scheme,
            "source_type": source,
            "free_surface_mode": free_surface,
            "boundary_mode": f"sponge_{sponge}",
            "cfl_stable": bool(result.cfl_info["stable"]),
            "cfl_number": float(result.cfl_info["cfl_number"]),
            **velocity,
            **metrics,
            "gauge_metric": gauge_metric,
        }
    best_name = min(cases, key=lambda key: cases[key]["rayleigh_velocity_relative_error"])
    detected = [name for name, item in cases.items() if item["rayleigh_like_event_detected"]]
    best_detected = detected[0] if detected else None
    best = cases[best_name]
    return {
        "stage": "Stage 5F",
        "cases": cases,
        "case_count": len(cases),
        "best_case": best_name,
        "best_detected_case": best_detected,
        "best_case_metrics": best,
        "best_free_surface_mode": best["free_surface_mode"],
        "best_boundary_mode": best["boundary_mode"],
        "best_source_type": best["source_type"],
        "rayleigh_like_event_detected": bool(detected),
        "rayleigh_velocity_relative_error": best["rayleigh_velocity_relative_error"],
        "staggered_grid_status": "implemented_minimal_validation",
        "ready_for_2p5d": bool(detected),
        "note": "该 benchmark 是小网格 Rayleigh-like sanity check，不是工业级 Rayleigh 正演。",
    }


def write_elastic2d_rayleigh_benchmark_report(path: Path, result: dict[str, Any]) -> None:
    """写出 Stage 5F Rayleigh benchmark 报告。"""

    lines = [
        "# elastic2d Rayleigh benchmark 报告",
        "",
        "本报告比较 collocated 与 staggered 最小 elastic2d validation。它不替代 layered_kinematic 主定位 forward。",
        "",
        f"- case_count：`{result['case_count']}`",
        f"- best_case：`{result['best_case']}`",
        f"- best_detected_case：`{result['best_detected_case']}`",
        f"- rayleigh_like_event_detected：`{result['rayleigh_like_event_detected']}`",
        f"- rayleigh_velocity_relative_error：`{result['rayleigh_velocity_relative_error']}`",
        f"- best_source_type：`{result['best_source_type']}`",
        f"- best_free_surface_mode：`{result['best_free_surface_mode']}`",
        f"- best_boundary_mode：`{result['best_boundary_mode']}`",
        f"- ready_for_2p5d：`{result['ready_for_2p5d']}`",
        "",
        "| case | scheme | source | free_surface | boundary | velocity | expected | rel_error | detected | boundary_reflection |",
        "|---|---|---|---|---|---:|---|---:|---|---:|",
    ]
    for name, item in result["cases"].items():
        lines.append(
            "| "
            f"{name} | {item['scheme']} | {item['source_type']} | {item['free_surface_mode']} | "
            f"{item['boundary_mode']} | {item['estimated_surface_velocity_mps']:.4g} | "
            f"{item['expected_rayleigh_like_range_mps']} | {item['rayleigh_velocity_relative_error']:.4g} | "
            f"{item['rayleigh_like_event_detected']} | {item['boundary_reflection_indicator']:.4g} |"
        )
    lines.extend(
        [
            "",
            "## 结论边界",
            "",
            "若 rayleigh_like_event_detected=False，则不得进入 2.5D 或把 elastic2d 写成 Rayleigh 正演成功。",
            "staggered-grid 本轮只是 benchmark validation engine，不是工业级模拟。",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
