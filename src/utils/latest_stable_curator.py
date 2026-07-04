"""Stage 5G latest_stable 三类结果数量审计。"""

from __future__ import annotations

from pathlib import Path
from typing import Any


FIGURE_LIMITS = {
    "forward": (8, 10),
    "localization": (5, 7),
    "error_analysis": (5, 7),
}

ANIMATION_LIMITS = {
    "forward": (2, 2),
    "localization": (0, 1),
    "error_analysis": (0, 1),
}

REPORT_LIMITS = {
    "forward": (3, 5),
    "localization": (1, 3),
    "error_analysis": (4, 6),
}


def _count_files(latest: Path, group: str, suffix: str, categories: dict[str, tuple[int, int]]) -> dict[str, int]:
    return {
        category: len(list((latest / group / category).glob(f"*{suffix}")))
        for category in categories
    }


def _outside_window(counts: dict[str, int], limits: dict[str, tuple[int, int]]) -> dict[str, int]:
    return {
        category: count
        for category, count in counts.items()
        if count < limits[category][0] or count > limits[category][1]
    }


def audit_latest_stable_files(latest_stable_dir: Path) -> dict[str, Any]:
    """统计 Stage 5G latest_stable 三类目录数量。"""

    latest = Path(latest_stable_dir)
    figure_counts = _count_files(latest, "figures", ".png", FIGURE_LIMITS)
    animation_counts = _count_files(latest, "animations", ".gif", ANIMATION_LIMITS)
    report_counts = _count_files(latest, "reports", ".md", REPORT_LIMITS)
    total_figures = sum(figure_counts.values())
    total_animations = sum(animation_counts.values())
    total_reports = sum(report_counts.values())
    root_png_count = len(list((latest / "figures").glob("*.png")))
    root_gif_count = len(list((latest / "animations").glob("*.gif"))) if (latest / "animations").exists() else 0
    over_or_under_figures = _outside_window(figure_counts, FIGURE_LIMITS)
    over_or_under_animations = _outside_window(animation_counts, ANIMATION_LIMITS)
    over_or_under_reports = _outside_window(report_counts, REPORT_LIMITS)
    unexpected_dirs = []
    for group in ["figures", "animations", "reports"]:
        root = latest / group
        if root.exists():
            for path in root.iterdir():
                if path.is_dir() and path.name not in {"forward", "localization", "error_analysis"}:
                    unexpected_dirs.append(f"{group}/{path.name}")
    status = (
        "pass"
        if not over_or_under_figures
        and not over_or_under_animations
        and not over_or_under_reports
        and 18 <= total_figures <= 24
        and 2 <= total_animations <= 4
        and 8 <= total_reports <= 12
        and root_png_count == 0
        and root_gif_count == 0
        and not unexpected_dirs
        else "warning"
    )
    return {
        "stage": "Stage 5G",
        "figure_counts": figure_counts,
        "animation_counts": animation_counts,
        "report_counts": report_counts,
        "latest_stable_total_figure_count": total_figures,
        "latest_stable_total_animation_count": total_animations,
        "latest_stable_total_report_count": total_reports,
        "figures_root_png_count": root_png_count,
        "animations_root_gif_count": root_gif_count,
        "out_of_range_figures": over_or_under_figures,
        "out_of_range_animations": over_or_under_animations,
        "out_of_range_reports": over_or_under_reports,
        "unexpected_dirs": unexpected_dirs,
        "status": status,
    }


def write_latest_stable_file_audit_report(path: Path, result: dict[str, Any]) -> None:
    """写出 latest_stable 三类精选审计报告。"""

    lines = [
        "# latest_stable 三类精选审计报告",
        "",
        f"- 阶段：`{result['stage']}`",
        f"- 静态图总数：`{result['latest_stable_total_figure_count']}`",
        f"- 动图总数：`{result['latest_stable_total_animation_count']}`",
        f"- 报告总数：`{result['latest_stable_total_report_count']}`",
        f"- figures 根目录 PNG 数量：`{result['figures_root_png_count']}`",
        f"- animations 根目录 GIF 数量：`{result['animations_root_gif_count']}`",
        f"- 非三类目录：`{result['unexpected_dirs']}`",
        f"- 状态：`{result['status']}`",
        "",
        "## 静态图数量",
        "",
    ]
    for category, count in result["figure_counts"].items():
        lines.append(f"- `{category}`：`{count}`")
    lines.extend(["", "## 动图数量", ""])
    for category, count in result["animation_counts"].items():
        lines.append(f"- `{category}`：`{count}`")
    lines.extend(["", "## 报告数量", ""])
    for category, count in result["report_counts"].items():
        lines.append(f"- `{category}`：`{count}`")
    lines.extend(
        [
            "",
            f"- 超出或低于范围的图件分类：`{result['out_of_range_figures']}`",
            f"- 超出或低于范围的动图分类：`{result['out_of_range_animations']}`",
            f"- 超出或低于范围的报告分类：`{result['out_of_range_reports']}`",
            "",
            "Stage 5G 的 latest_stable 只服务人工查看当前进度，不作为历史输出仓库。",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
