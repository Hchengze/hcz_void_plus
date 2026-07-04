"""elastic2d 数值格式敏感性验证。

Stage 5D 已经说明 Rayleigh-like 检测未通过。本模块不做大规模参数搜索，而是用
轻量 one-factor-at-a-time 对照检查失败可能来自震源、边界、自由表面、接收深度
还是拾取窗口。所有结果仅服务 validation forward，不改变 layered_kinematic 主定位。
"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.validation.common import clone_params
from src.validation.elastic2d_rayleigh_validation import run_elastic2d_rayleigh_validation


def _case_params(params, case: dict[str, Any]):
    """构建单个敏感性 case 的参数副本。"""

    trial = clone_params(params)
    for key, value in case.items():
        setattr(trial.forward, key, value)
    return trial


def _surface_event_metrics(validation: dict[str, Any]) -> dict[str, float]:
    """从 surface gather 提取简单数值诊断。

    指标只用于比较不同数值设置的趋势：
        surface_event_energy: 拾取窗口附近的表面能量；
        body_wave_leakage_indicator: 极早时窗能量占比，偏高可能代表体波/近源强事件；
        boundary_reflection_indicator: 记录尾段能量占比，偏高可能代表边界反射或尾波。
    """

    result = validation["elastic_result"]
    gather = np.asarray(result.surface_vz_gather, dtype=float)
    total = float(np.sum(gather * gather))
    if total <= 0.0:
        return {
            "surface_event_energy": 0.0,
            "body_wave_leakage_indicator": 0.0,
            "boundary_reflection_indicator": 0.0,
            "max_amplitude": 0.0,
        }
    nt = gather.shape[0]
    early = gather[: max(1, nt // 8), :]
    late = gather[int(0.75 * nt) :, :]
    picked = np.asarray(validation.get("pick_time_s") or [], dtype=float)
    time_axis = np.asarray(result.time_axis_s, dtype=float)
    dt = float(time_axis[1] - time_axis[0]) if len(time_axis) > 1 else 1.0
    half = max(1, int(round(0.003 / dt)))
    surface_energy = 0.0
    if picked.size:
        for ich, t_s in enumerate(picked[: gather.shape[1]]):
            if t_s <= 0.0:
                continue
            center = int(round(t_s / dt))
            start = max(0, center - half)
            stop = min(nt, center + half + 1)
            surface_energy += float(np.sum(gather[start:stop, ich] ** 2))
    return {
        "surface_event_energy": surface_energy,
        "body_wave_leakage_indicator": float(np.sum(early * early) / total),
        "boundary_reflection_indicator": float(np.sum(late * late) / total),
        "max_amplitude": float(np.max(np.abs(gather))),
    }


def _case_matrix() -> list[dict[str, Any]]:
    """返回轻量敏感性矩阵。

    这里不是全组合扫描，而是从 baseline 出发逐项替换，保证每个用户关心的取值
    至少被检查一次，同时控制 full_pipeline 运行时间。
    """

    baseline = {
        "name": "baseline_vertical_depth0.2_medium_approx_surface",
        "elastic2d_source_type": "vertical_force",
        "elastic2d_source_depth_m": 0.2,
        "elastic2d_sponge_strength_mode": "medium",
        "elastic2d_free_surface_mode": "approximate",
        "elastic2d_receiver_depth_index": "surface",
    }
    variants = [
        {"name": "source_horizontal", "elastic2d_source_type": "horizontal_force"},
        {"name": "source_explosive", "elastic2d_source_type": "explosive"},
        {"name": "source_depth0.1", "elastic2d_source_depth_m": 0.1},
        {"name": "source_depth0.4", "elastic2d_source_depth_m": 0.4},
        {"name": "sponge_weak", "elastic2d_sponge_strength_mode": "weak"},
        {"name": "sponge_strong", "elastic2d_sponge_strength_mode": "strong"},
        {"name": "free_surface_stress_zero_variant", "elastic2d_free_surface_mode": "stress_zero_variant"},
        {"name": "receiver_one_grid_below", "elastic2d_receiver_depth_index": "one_grid_below_surface"},
    ]
    cases = [baseline]
    for variant in variants:
        case = dict(baseline)
        case.update(variant)
        cases.append(case)
    return cases


def run_elastic2d_numerical_sensitivity(params) -> dict[str, Any]:
    """运行 elastic2d 小规模数值敏感性验证。"""

    cases: dict[str, dict[str, Any]] = {}
    for case in _case_matrix():
        name = case["name"]
        trial = _case_params(params, {key: value for key, value in case.items() if key != "name"})
        validation = run_elastic2d_rayleigh_validation(trial)
        metrics = _surface_event_metrics(validation)
        expected_min, expected_max = validation["expected_rayleigh_like_range_mps"]
        expected_center = 0.5 * (expected_min + expected_max)
        velocity = float(validation["estimated_surface_velocity_mps"])
        cases[name] = {
            "name": name,
            "source_type": trial.forward.elastic2d_source_type,
            "source_depth_m": trial.forward.elastic2d_source_depth_m,
            "sponge_strength": trial.forward.elastic2d_sponge_strength_mode,
            "free_surface_mode": trial.forward.elastic2d_free_surface_mode,
            "receiver_depth_index": trial.forward.elastic2d_receiver_depth_index,
            "estimated_surface_velocity_mps": velocity,
            "expected_rayleigh_like_range_mps": validation["expected_rayleigh_like_range_mps"],
            "rayleigh_like_event_detected": validation["rayleigh_like_event_detected"],
            "rayleigh_pick_interpretation": validation["rayleigh_pick_interpretation"],
            "surface_event_energy": metrics["surface_event_energy"],
            "body_wave_leakage_indicator": metrics["body_wave_leakage_indicator"],
            "boundary_reflection_indicator": metrics["boundary_reflection_indicator"],
            "cfl": validation["cfl_info"]["cfl_number"],
            "cfl_stable": validation["cfl_info"]["stable"],
            "max_amplitude": metrics["max_amplitude"],
            "distance_to_expected_center_mps": abs(velocity - expected_center),
        }
    detected = [name for name, item in cases.items() if item["rayleigh_like_event_detected"]]
    if detected:
        best_name = max(detected, key=lambda key: cases[key]["surface_event_energy"])
    else:
        best_name = min(cases, key=lambda key: cases[key]["distance_to_expected_center_mps"])
    best = cases[best_name]
    likely_cause = "picking_or_boundary"
    if best["body_wave_leakage_indicator"] > 0.5:
        likely_cause = "body_wave_or_near_source_dominance"
    elif best["boundary_reflection_indicator"] > 0.25:
        likely_cause = "boundary_reflection_or_late_coda"
    elif not best["rayleigh_like_event_detected"]:
        likely_cause = "free_surface_or_collocated_grid_limit"
    return {
        "cases": cases,
        "case_count": len(cases),
        "best_case": best_name,
        "best_case_metrics": best,
        "rayleigh_like_event_best_case": best["rayleigh_like_event_detected"],
        "rayleigh_like_event_detected_any": bool(detected),
        "likely_failure_cause": likely_cause,
        "elastic2d_ready_for_2p5d": bool(detected and best["boundary_reflection_indicator"] < 0.25),
        "note": "该敏感性验证是轻量 one-factor-at-a-time 矩阵，不是 elastic2d 参数反演。",
    }


def write_elastic2d_numerical_sensitivity_report(path, result: dict[str, Any]) -> None:
    """写出 elastic2d 数值敏感性报告。"""

    best = result["best_case_metrics"]
    lines = [
        "# elastic2d 数值敏感性报告",
        "",
        "本报告比较 source、source depth、sponge、free-surface 和 receiver depth 对 Rayleigh-like 拾取的影响。",
        "所有结果仅服务 validation forward；layered_kinematic 仍是当前主定位 forward。",
        "",
        f"- case_count：`{result['case_count']}`",
        f"- best_case：`{result['best_case']}`",
        f"- best estimated velocity：`{best['estimated_surface_velocity_mps']}` m/s",
        f"- expected range：`{best['expected_rayleigh_like_range_mps']}` m/s",
        f"- rayleigh_like_event_detected_any：`{result['rayleigh_like_event_detected_any']}`",
        f"- likely_failure_cause：`{result['likely_failure_cause']}`",
        f"- elastic2d_ready_for_2p5d：`{result['elastic2d_ready_for_2p5d']}`",
        "",
        "| case | source | depth | sponge | free_surface | receiver | velocity | detected | body leakage | boundary reflection |",
        "|---|---|---:|---|---|---|---:|---|---:|---:|",
    ]
    for name, item in result["cases"].items():
        lines.append(
            "| "
            f"{name} | {item['source_type']} | {item['source_depth_m']} | "
            f"{item['sponge_strength']} | {item['free_surface_mode']} | {item['receiver_depth_index']} | "
            f"{item['estimated_surface_velocity_mps']:.4g} | {item['rayleigh_like_event_detected']} | "
            f"{item['body_wave_leakage_indicator']:.4g} | {item['boundary_reflection_indicator']:.4g} |"
        )
    lines.extend(
        [
            "",
            "## 解释边界",
            "",
            "若 Rayleigh-like 检测未通过，本报告不得被写成 Rayleigh 正演成功。",
            "当前 collocated-grid prototype 的自由表面、sponge 和拾取逻辑仍需继续硬化；未通过前不建议进入 2.5D。",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
