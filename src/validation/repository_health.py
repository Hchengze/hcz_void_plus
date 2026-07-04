"""仓库与 latest_stable 健康报告。

本模块把 Stage 5D/5E/5F 开场核验固化为报告：HEAD、summary commit、latest_stable
分层数量、根目录是否平铺图件、文本换行健康等。报告明确说明：若 GitHub 网页
预览与本地结果不同，以 git ls-tree 与本地字节检查为准。
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from tools.check_text_health import collect_text_health, default_paths


def _git_short_head(repo_root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            check=True,
            text=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return completed.stdout.strip() or "unknown"


def _summary_commit(summary_path: Path) -> str:
    if not summary_path.exists():
        return "missing"
    for line in summary_path.read_text(encoding="utf-8").splitlines():
        if "commit id" in line and "`" in line:
            return line.split("`")[1]
    return "unknown"


def _count_files(path: Path, pattern: str) -> int:
    if not path.exists():
        return 0
    return len(list(path.glob(pattern)))


def build_repository_health_report(repo_root: Path, latest_stable_dir: Path) -> dict[str, Any]:
    """汇总仓库和 latest_stable 健康状态。"""

    repo_root = Path(repo_root)
    latest = Path(latest_stable_dir)
    text_health_raw = collect_text_health(default_paths(repo_root))
    text_health = [
        {
            "path": item.path,
            "relative_path": Path(item.path).resolve().relative_to(repo_root.resolve()).as_posix(),
            "logical_line_count": item.logical_line_count,
            "cr_only": item.cr_only_count,
            "longest_line": item.longest_line_length,
            "healthy": item.healthy,
        }
        for item in text_health_raw
    ]
    categories = ["forward", "localization", "error_analysis"]
    figure_counts = {
        category: _count_files(latest / "figures" / category, "*")
        for category in categories
    }
    report_counts = {
        category: _count_files(latest / "reports" / category, "*.md")
        for category in categories
    }
    cr_only_files = [item["relative_path"] for item in text_health if item["cr_only"] > 0]
    one_line_files = [item["relative_path"] for item in text_health if item["logical_line_count"] < 5]
    head = _git_short_head(repo_root)
    summary_commit = _summary_commit(latest / "summary.md")
    return {
        "head_commit": head,
        "latest_stable_summary_commit": summary_commit,
        "latest_stable_stage5g": "Stage 5G" in (latest / "summary.md").read_text(encoding="utf-8")
        if (latest / "summary.md").exists()
        else False,
        "latest_stable_old_stage_marker": any(
            marker in (latest / "summary.md").read_text(encoding="utf-8")
            for marker in ["Stage 3 主结论", "Stage 4 主结论", "Stage 5A 主结论"]
        )
        if (latest / "summary.md").exists()
        else False,
        "figures_root_png_count": _count_files(latest / "figures", "*.png"),
        "figure_counts": figure_counts,
        "reports_root_md_count": _count_files(latest / "reports", "*.md"),
        "report_counts": report_counts,
        "text_health": text_health,
        "cr_only_files": cr_only_files,
        "one_line_files": one_line_files,
        "github_vs_local_note": (
            "GitHub 网页 raw/preview 可能受编码或浏览器渲染影响；本报告以 git ls-tree、"
            "本地字节换行和 Python UTF-8 读取结果为准。"
        ),
        "status": "pass"
        if _count_files(latest / "figures", "*.png") == 0 and not cr_only_files and not one_line_files
        else "warning",
    }


def write_repository_health_report(path: Path, result: dict[str, Any]) -> None:
    """写出 repository health 报告。"""

    lines = [
        "# repository health 报告",
        "",
        f"- 当前 HEAD commit：`{result['head_commit']}`",
        f"- latest_stable summary commit：`{result['latest_stable_summary_commit']}`",
        f"- latest_stable 是否为 Stage 5G：`{result['latest_stable_stage5g']}`",
        f"- latest_stable 是否混入旧阶段主结论：`{result['latest_stable_old_stage_marker']}`",
        f"- figures 根目录 PNG 数量：`{result['figures_root_png_count']}`",
        f"- reports 根目录 MD 数量：`{result['reports_root_md_count']}`",
        f"- 状态：`{result['status']}`",
        "",
        "## figures 分层数量",
        "",
    ]
    for category, count in result["figure_counts"].items():
        lines.append(f"- `{category}`：`{count}`")
    lines.extend(["", "## reports 分层数量", ""])
    for category, count in result["report_counts"].items():
        lines.append(f"- `{category}`：`{count}`")
    lines.extend(
        [
            "",
            "## text health 关键统计",
            "",
            "| file | lines | cr_only | longest | healthy |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for item in result["text_health"]:
        lines.append(
            f"| `{item['relative_path']}` | {item['logical_line_count']} | "
            f"{item['cr_only']} | {item['longest_line']} | {item['healthy']} |"
        )
    lines.extend(
        [
            "",
            f"- CR-only 文件：`{result['cr_only_files']}`",
            f"- 真实一行化/极少行文件：`{result['one_line_files']}`",
            "",
            result["github_vs_local_note"],
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
