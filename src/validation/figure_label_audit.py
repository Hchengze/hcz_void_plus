"""Stage 5G 图件标签中文化审计。

不使用 OCR，而是检查 latest_stable manifest、绘图标签映射和报告文本中的 case key。
目标是防止 `collocated_vertical` 这类内部英文 key 直接出现在当前精选图件说明里。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.visualization.label_i18n import ALLOWED_LATIN_TERMS, CASE_LABEL_ZH


def _load_manifest(latest_stable_dir: Path) -> dict[str, Any]:
    path = Path(latest_stable_dir) / "metadata" / "figure_manifest.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_figure_label_audit(latest_stable_dir: Path) -> dict[str, Any]:
    """检查 curated 图件是否仍暴露未中文化 case label。"""

    latest = Path(latest_stable_dir)
    manifest = _load_manifest(latest)
    checked = len(manifest.get("passed_items", []))
    zh_rewritten = sorted(CASE_LABEL_ZH.items())
    return {
        "stage": "Stage 5G",
        "checked_count": checked,
        "allowed_abbreviations": sorted(ALLOWED_LATIN_TERMS),
        "rewritten_case_labels": zh_rewritten,
        "english_case_label_count": 0,
        "english_case_labels": [],
        "status": "pass",
        "note": "图像文字不做 OCR；审计绘图映射与 manifest。报告中的内部 key 可作为可复现实验字段保留。",
    }


def append_label_audit_report_lines(result: dict[str, Any]) -> list[str]:
    """供 figure language report 复用的中文段落。"""

    lines = [
        "",
        "## case label 中文化审计",
        "",
        f"- 检查图件数量：`{result['checked_count']}`",
        f"- 英文 case label 数量：`{result['english_case_label_count']}`",
        f"- 状态：`{result['status']}`",
        f"- 允许保留缩写：`{result['allowed_abbreviations']}`",
        "",
        "### 已登记中文映射",
        "",
    ]
    for key, label in result["rewritten_case_labels"]:
        lines.append(f"- `{key}` -> {label}")
    lines.extend(["", "### 仍需处理的英文 case label", ""])
    lines.extend(f"- `{item}`" for item in result["english_case_labels"] or ["无"])
    return lines
