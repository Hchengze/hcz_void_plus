"""Stage 5H 人工复查入口检查。

本模块不再为每一张图写单独测试，而是检查 summary 中的
manual_review_figures / manual_review_animations 是否真实、受控、属于
forward/localization/error_analysis 三类，并确认关键三维图和动图没有被误归档。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


ALLOWED_CATEGORIES = {"forward", "localization", "error_analysis"}

REQUIRED_3D_FIGURES = {
    "figures/forward/fig_geometry_3d_overview.png",
    "figures/localization/fig_3d_high_score_region.png",
    "figures/localization/fig_recommended_location_3d.png",
    "figures/localization/fig_3d_uncertainty_box.png",
}

REQUIRED_ANIMATIONS = {
    "animations/forward/anim_multishot_forward_overview.gif",
    "animations/forward/anim_single_shot_wavefield.gif",
}

RECOMMENDED_REVIEW_ORDER = [
    "figures/error_analysis/fig_stage5h_status_badge.png",
    "figures/forward/fig_geometry_3d_overview.png",
    "animations/forward/anim_multishot_forward_overview.gif",
    "animations/forward/anim_single_shot_wavefield.gif",
    "figures/forward/fig_velocity_model_active_badge.png",
    "figures/forward/fig_velocity_model_physics_bridge.png",
    "figures/forward/fig_elastic2d_rayleigh_benchmark_matrix.png",
    "figures/forward/fig_elastic2d_das_best_case.png",
    "figures/localization/fig_3d_high_score_region.png",
    "figures/localization/fig_recommended_location_3d.png",
    "figures/localization/fig_3d_uncertainty_box.png",
    "figures/error_analysis/fig_rayleigh_pick_interpretation.png",
]


def _extract_list(summary_text: str, heading: str) -> list[str]:
    """从 summary 的指定标题下提取 Markdown 列表。

    这里采用简单而可审计的 Markdown 解析：只读取 ``## heading`` 到下一个二级标题
    之间以 ``- `` 开头的条目。summary 是本项目自己生成的稳定格式，没必要引入
    额外 Markdown 解析依赖。
    """

    lines = summary_text.splitlines()
    capture = False
    items: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == f"## {heading}":
            capture = True
            continue
        if capture and stripped.startswith("## "):
            break
        if capture and stripped.startswith("- "):
            items.append(stripped[2:].strip().strip("`"))
    return items


def _category(rel_path: str) -> str | None:
    parts = Path(rel_path).parts
    if len(parts) >= 3 and parts[0] in {"figures", "animations"}:
        return parts[1]
    return None


def run_manual_review_readiness(latest_stable_dir: Path) -> dict[str, Any]:
    """检查 latest_stable 是否已经适合人工按清单复查。"""

    latest = Path(latest_stable_dir)
    summary_path = latest / "summary.md"
    summary_text = summary_path.read_text(encoding="utf-8") if summary_path.exists() else ""
    figures = _extract_list(summary_text, "manual_review_figures")
    animations = _extract_list(summary_text, "manual_review_animations")

    failures: list[str] = []
    warnings: list[str] = []

    if not (8 <= len(figures) <= 10):
        failures.append(f"manual_review_figures 数量为 {len(figures)}，应控制在 8-10 张。")
    if not (2 <= len(animations) <= 4):
        failures.append(f"manual_review_animations 数量为 {len(animations)}，应控制在 2-4 个。")

    missing_figures = [rel for rel in figures if not (latest / rel).exists()]
    missing_animations = [rel for rel in animations if not (latest / rel).exists()]
    if missing_figures:
        failures.append(f"manual_review_figures 引用不存在文件：{missing_figures}")
    if missing_animations:
        failures.append(f"manual_review_animations 引用不存在文件：{missing_animations}")

    bad_categories = [
        rel for rel in figures + animations if _category(rel) not in ALLOWED_CATEGORIES
    ]
    if bad_categories:
        failures.append(f"manual_review 清单包含非三类目录：{bad_categories}")

    missing_3d = sorted(rel for rel in REQUIRED_3D_FIGURES if rel not in figures)
    if missing_3d:
        failures.append(f"manual_review_figures 缺少关键三维图：{missing_3d}")

    missing_required_anim = sorted(rel for rel in REQUIRED_ANIMATIONS if rel not in animations)
    if missing_required_anim:
        failures.append(f"manual_review_animations 缺少关键动图：{missing_required_anim}")

    animation_sizes = {}
    for rel in animations:
        path = latest / rel
        size = path.stat().st_size if path.exists() else 0
        animation_sizes[rel] = size
        if size < 4096:
            failures.append(f"动图过小或近似空 GIF：{rel} ({size} bytes)")

    archived_hits = [rel for rel in figures + animations if "core/" in rel or "diagnostics/" in rel or "uncertainty/" in rel]
    if archived_hits:
        failures.append(f"manual_review 清单引用旧分类目录：{archived_hits}")

    existing_review_order = [rel for rel in RECOMMENDED_REVIEW_ORDER if (latest / rel).exists()]
    if len(existing_review_order) < 10:
        warnings.append("人工建议查看顺序中存在缺失项，请检查 latest_stable 精选清单。")

    return {
        "stage": "Stage 5H",
        "manual_review_figure_count": len(figures),
        "manual_review_animation_count": len(animations),
        "manual_review_figures": figures,
        "manual_review_animations": animations,
        "animation_sizes_bytes": animation_sizes,
        "required_3d_figures_present": not missing_3d,
        "required_animations_present": not missing_required_anim,
        "recommended_review_order": existing_review_order,
        "warnings": warnings,
        "failures": failures,
        "status": "pass" if not failures else "fail",
    }


def write_manual_review_readiness_report(path: Path, result: dict[str, Any]) -> None:
    """写出人工复查准备度报告。"""

    lines = [
        "# manual review readiness 报告",
        "",
        "本报告检查 Stage 5H 的人工复查入口是否清晰、受控、真实存在。",
        "",
        f"- stage：`{result['stage']}`",
        f"- manual_review_figures 数量：`{result['manual_review_figure_count']}`",
        f"- manual_review_animations 数量：`{result['manual_review_animation_count']}`",
        f"- 关键三维图齐全：`{result['required_3d_figures_present']}`",
        f"- 关键动图齐全：`{result['required_animations_present']}`",
        f"- 状态：`{result['status']}`",
        "",
        "## 人工建议查看顺序",
        "",
    ]
    lines.extend(f"{index}. `{item}`" for index, item in enumerate(result["recommended_review_order"], start=1))
    lines.extend(["", "## 动图大小", ""])
    lines.extend(f"- `{name}`：`{size}` bytes" for name, size in result["animation_sizes_bytes"].items())
    lines.extend(["", "## warnings", ""])
    lines.extend(f"- {item}" for item in result["warnings"] or ["无"])
    lines.extend(["", "## failures", ""])
    lines.extend(f"- {item}" for item in result["failures"] or ["无"])
    lines.extend(
        [
            "",
            "## 解释边界",
            "",
            "这些图件表达三维几何与定位表达、三维运动学定位结果，不代表当前 elastic2d 已经是三维弹性正演。",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
