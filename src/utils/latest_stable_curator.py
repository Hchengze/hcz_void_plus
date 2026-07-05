"""Stage 5I latest_stable 三类结果数量和目录快照审计。"""

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
    """统计 Stage 5I latest_stable 三类目录数量。"""

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
        "stage": "Stage 5I",
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
            "Stage 5I 的 latest_stable 只服务人工查看当前三维运动学反演进度，不作为历史输出仓库。",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_latest_stable_tree_snapshot(latest_stable_dir: Path) -> dict[str, Any]:
    """构建当前 latest_stable 的文件树快照。

    优先使用本地文件系统而不是网页预览。报告中明确说明：如果 Git diff 中出现
    core/diagnostics/uncertainty 等旧目录，那只是历史删除或移动痕迹，不代表当前
    latest_stable 仍保留这些目录。
    """

    latest = Path(latest_stable_dir)
    rows: list[str] = []
    if latest.exists():
        for path in sorted(latest.rglob("*")):
            if path.is_file():
                rel = path.relative_to(latest.parent).as_posix()
                rows.append(rel)

    old_dirs = []
    for group in ["figures", "animations", "reports"]:
        for old in ["core", "diagnostics", "uncertainty", "reference_only"]:
            if (latest / group / old).exists():
                old_dirs.append(f"{group}/{old}")

    figure_counts = {
        category: len(list((latest / "figures" / category).glob("*.png")))
        for category in FIGURE_LIMITS
    }
    animation_counts = {
        category: len(list((latest / "animations" / category).glob("*.gif")))
        for category in ANIMATION_LIMITS
    }
    report_counts = {
        category: len(list((latest / "reports" / category).glob("*.md")))
        for category in REPORT_LIMITS
    }
    return {
        "stage": "Stage 5I",
        "tree_lines": rows,
        "figure_counts": figure_counts,
        "animation_counts": animation_counts,
        "report_counts": report_counts,
        "old_category_dirs_present": old_dirs,
        "status": "pass" if not old_dirs else "warning",
    }


def write_latest_stable_tree_snapshot(snapshot_path: Path, result: dict[str, Any]) -> None:
    """写出可供人工和测试读取的 latest_stable 文件树快照。"""

    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text("\n".join(result["tree_lines"]) + "\n", encoding="utf-8")


def write_latest_stable_tree_snapshot_report(path: Path, result: dict[str, Any]) -> None:
    """写出 latest_stable tree snapshot 报告。"""

    lines = [
        "# latest_stable tree snapshot 报告",
        "",
        "本报告来自当前本地文件树。若 commit diff 中出现旧目录，只说明它们是历史删除/移动痕迹，",
        "不代表当前 latest_stable 结构仍包含旧分类。",
        "",
        f"- stage：`{result['stage']}`",
        f"- figures/forward 图件数量：`{result['figure_counts'].get('forward')}`",
        f"- figures/localization 图件数量：`{result['figure_counts'].get('localization')}`",
        f"- figures/error_analysis 图件数量：`{result['figure_counts'].get('error_analysis')}`",
        f"- animations/forward 动图数量：`{result['animation_counts'].get('forward')}`",
        f"- 旧目录 core/diagnostics/uncertainty/reference_only 是否存在：`{bool(result['old_category_dirs_present'])}`",
        f"- 旧目录清单：`{result['old_category_dirs_present']}`",
        f"- 状态：`{result['status']}`",
        "",
        "## 当前文件树",
        "",
    ]
    lines.extend(f"- `{line}`" for line in result["tree_lines"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
