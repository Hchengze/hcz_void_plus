"""科学图件自检。

Stage 5D 的 figure self-check 主要检查文件是否存在、能否读取、是否空白。Stage 5E
进一步检查“图件、报告和 summary 的科学结论是否一致”。该模块不做图像语义识别，
而是基于 manifest、summary_info 和报告文本进行可审计规则检查。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


RECOMMENDED_STAGE5F_FIGURES = [
    "figures/core/fig_stage5f_status_badge.png",
    "figures/core/fig_confidence_diagnostics.png",
    "figures/diagnostics/fig_velocity_model_active_badge.png",
    "figures/diagnostics/fig_latest_stable_quality_summary.png",
    "figures/diagnostics/fig_velocity_model_physics_bridge.png",
    "figures/forward/fig_elastic2d_rayleigh_benchmark_matrix.png",
    "figures/forward/fig_elastic2d_rayleigh_velocity_error.png",
    "figures/forward/fig_elastic2d_surface_event_ridge.png",
    "figures/forward/fig_elastic2d_das_best_case.png",
    "figures/forward/fig_elastic_vs_kinematic_energy_partition.png",
    "figures/localization/fig_scan_x_y_slice.png",
]

# 兼容 Stage 5E 测试导入名；当前推荐清单已切换到 Stage 5F。
RECOMMENDED_STAGE5E_FIGURES = RECOMMENDED_STAGE5F_FIGURES


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _all_report_text(latest_stable_dir: Path) -> str:
    parts = [_read_text(latest_stable_dir / "summary.md")]
    reports = latest_stable_dir / "reports"
    if reports.exists():
        for path in sorted(reports.glob("*/*.md")):
            parts.append(_read_text(path))
    return "\n".join(parts)


def _load_manifest(latest_stable_dir: Path) -> dict[str, Any]:
    path = latest_stable_dir / "metadata" / "figure_manifest.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _contains_unqualified_phrase(text: str, phrase: str) -> bool:
    """判断文本是否包含未被否定语境约束的成功表述。

    报告中允许写“不得宣称 Rayleigh 正演成功”这类边界说明；真正需要阻止的是
    在 Rayleigh 或 DAS 诊断未通过时，把失败结果写成肯定成功。
    """

    start = 0
    negation_markers = ["不得", "不能", "不应", "未", "禁止", "不可"]
    while True:
        index = text.find(phrase, start)
        if index < 0:
            return False
        prefix = text[max(0, index - 32) : index]
        if not any(marker in prefix for marker in negation_markers):
            return True
        start = index + len(phrase)


def run_scientific_figure_self_check(latest_stable_dir: Path, summary_info: dict[str, Any]) -> dict[str, Any]:
    """执行科学结论自检。"""

    latest = Path(latest_stable_dir)
    manifest = _load_manifest(latest)
    items = manifest.get("passed_items", [])
    warnings: list[str] = []
    failures: list[str] = []
    text = _all_report_text(latest)

    for item in items:
        metadata = item.get("metadata") or {}
        for key in ["stage", "forward_engine", "velocity_model_type"]:
            if key not in metadata:
                failures.append(f"{item.get('filename')} 缺少 metadata: {key}")
        if metadata.get("stage") and "Stage 3" in str(metadata.get("stage")):
            failures.append(f"{item.get('filename')} metadata 混入 Stage 3")

    rayleigh_detected = bool(summary_info.get("rayleigh_like_event_detected"))
    gauge_status = str(summary_info.get("das_gauge_nonzero_status") or "")
    active_velocity = str(summary_info.get("active_velocity_model_type") or "")
    forbidden_rayleigh_success = [
        "Rayleigh 正演成功",
        "Rayleigh-like 检测成功",
        "Rayleigh-like event detected: True",
    ]
    if not rayleigh_detected:
        for phrase in forbidden_rayleigh_success:
            if _contains_unqualified_phrase(text, phrase):
                failures.append(f"Rayleigh-like 未通过，但文本包含成功表述：{phrase}")
    forbidden_gauge_success = [
        "DAS gauge response 有效",
        "gauge strain 可用于默认定位",
        "真实 DAS 响应有效",
    ]
    if gauge_status in {"zero_or_too_weak", "0", "False", ""}:
        for phrase in forbidden_gauge_success:
            if _contains_unqualified_phrase(text, phrase):
                failures.append(f"DAS gauge 很弱或为零，但文本包含有效表述：{phrase}")
    if active_velocity == "layered":
        badge = latest / "figures" / "diagnostics" / "fig_velocity_model_active_badge.png"
        if not badge.exists():
            failures.append("active velocity model 为 layered，但缺少 velocity_model_active_badge 图件。")
        if "active_velocity_model_type：`layered`" not in _read_text(latest / "summary.md"):
            failures.append("summary 未明确 active_velocity_model_type=layered。")

    audit_text = _read_text(latest / "reports" / "diagnostics" / "report_velocity_model_audit.md")
    if active_velocity and f"active velocity_model_type：`{active_velocity}`" not in audit_text:
        failures.append("velocity model 图件/summary 与 velocity_model_audit 报告不一致。")

    for item in items:
        required_report = item.get("metadata", {}).get("required_report")
        if required_report in {
            "reports/core/report_latest_stable_file_audit.md",
            "reports/core/report_figure_quality_check.md",
            "reports/core/report_figure_deduplication.md",
            "reports/core/report_figure_language_check.md",
            "reports/core/report_scientific_figure_self_check.md",
        }:
            # scientific self-check 报告是在本函数运行后才写出，属于合法的自引用报告。
            continue
        if required_report and not (latest / required_report).exists():
            warnings.append(f"{item.get('filename')} 对应报告不存在：{required_report}")

    recommended_existing = [
        name for name in RECOMMENDED_STAGE5F_FIGURES if (latest / name).exists()
    ]
    if not (8 <= len(recommended_existing) <= 12):
        warnings.append(f"人工推荐图件数量为 {len(recommended_existing)}，不在 8-12 范围内。")
    return {
        "stage": "Stage 5F",
        "checked_figure_count": len(items),
        "passed_count": len(items) if not failures else max(0, len(items) - len(failures)),
        "scientific_warning_count": len(warnings),
        "failure_count": len(failures),
        "warnings": warnings,
        "failures": failures,
        "conclusion_consistent": not failures,
        "old_stage_conclusion_mixed": any("Stage 3" in failure or "Stage 4" in failure for failure in failures),
        "recommended_figures": recommended_existing,
        "status": "pass" if not failures else "fail",
    }


def write_scientific_figure_self_check_report(path: Path, result: dict[str, Any]) -> None:
    """写出科学图件自检报告。"""

    lines = [
        "# scientific figure self-check 报告",
        "",
        "本报告检查图件、报告和 summary 的科学结论是否一致。它不替代人工解释，",
        "但会阻止 Rayleigh 未通过却写成功、DAS gauge 很弱却写有效等结论错误进入 latest_stable。",
        "",
        f"- 检查图件数量：`{result['checked_figure_count']}`",
        f"- 通过数量：`{result['passed_count']}`",
        f"- scientific warning 数量：`{result['scientific_warning_count']}`",
        f"- failure 数量：`{result['failure_count']}`",
        f"- 结论与图件一致：`{result['conclusion_consistent']}`",
        f"- 旧阶段结论混入：`{result['old_stage_conclusion_mixed']}`",
        f"- 状态：`{result['status']}`",
        "",
        "## warnings",
        "",
    ]
    lines.extend(f"- {item}" for item in result["warnings"] or ["无。"])
    lines.extend(["", "## failures", ""])
    lines.extend(f"- {item}" for item in result["failures"] or ["无。"])
    lines.extend(["", "## 当前推荐人工查看图件", ""])
    lines.extend(f"- `{item}`" for item in result["recommended_figures"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
