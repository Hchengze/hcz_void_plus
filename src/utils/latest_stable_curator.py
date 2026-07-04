"""Stage 5F latest_stable 精选治理工具。"""

from __future__ import annotations

from pathlib import Path
from typing import Any


FIGURE_LIMITS = {
    "core": 6,
    "forward": 10,
    "localization": 6,
    "uncertainty": 5,
    "diagnostics": 8,
}


REPORT_LIMITS = {
    "core": 7,
    "forward": 6,
    "localization": 2,
    "uncertainty": 1,
    "diagnostics": 4,
}


def audit_latest_stable_files(latest_stable_dir: Path) -> dict[str, Any]:
    """统计 latest_stable 分层数量并判断是否符合 Stage 5F 精选上限。"""

    latest = Path(latest_stable_dir)
    figure_counts = {
        category: len(list((latest / "figures" / category).glob("*.png")))
        for category in FIGURE_LIMITS
    }
    report_counts = {
        category: len(list((latest / "reports" / category).glob("*.md")))
        for category in REPORT_LIMITS
    }
    total_figures = sum(figure_counts.values())
    total_reports = sum(report_counts.values())
    over_limit_figures = {
        category: count
        for category, count in figure_counts.items()
        if count > FIGURE_LIMITS[category]
    }
    over_limit_reports = {
        category: count
        for category, count in report_counts.items()
        if count > REPORT_LIMITS[category]
    }
    root_png_count = len(list((latest / "figures").glob("*.png")))
    status = (
        "pass"
        if not over_limit_figures
        and not over_limit_reports
        and 25 <= total_figures <= 35
        and 12 <= total_reports <= 18
        and root_png_count == 0
        else "warning"
    )
    return {
        "stage": "Stage 5F",
        "figure_counts": figure_counts,
        "report_counts": report_counts,
        "latest_stable_total_figure_count": total_figures,
        "latest_stable_total_report_count": total_reports,
        "figures_root_png_count": root_png_count,
        "over_limit_figures": over_limit_figures,
        "over_limit_reports": over_limit_reports,
        "status": status,
    }


def write_latest_stable_file_audit_report(path: Path, result: dict[str, Any]) -> None:
    """写出 latest_stable 文件精选审计报告。"""

    lines = [
        "# latest_stable 文件精选审计报告",
        "",
        f"- 图件总数：`{result['latest_stable_total_figure_count']}`",
        f"- 报告总数：`{result['latest_stable_total_report_count']}`",
        f"- figures 根目录 PNG 数量：`{result['figures_root_png_count']}`",
        f"- 状态：`{result['status']}`",
        "",
        "## 图件分层数量",
        "",
    ]
    for category, count in result["figure_counts"].items():
        lines.append(f"- `{category}`：`{count}`")
    lines.extend(["", "## 报告分层数量", ""])
    for category, count in result["report_counts"].items():
        lines.append(f"- `{category}`：`{count}`")
    lines.extend(
        [
            "",
            f"- 超限图件分类：`{result['over_limit_figures']}`",
            f"- 超限报告分类：`{result['over_limit_reports']}`",
            "",
            "latest_stable 只代表当前 Stage 5F 精选成果，不是历史输出仓库。",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
