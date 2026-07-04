"""Stage 5G latest_stable 图件语言检查。

当前不引入 OCR。语言检查基于 curated manifest、绘图函数约定和 case label 中文映射：
进入 latest_stable 的图件必须声明 `language=zh`，内部 case key 必须有中文展示标签。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.validation.figure_label_audit import append_label_audit_report_lines, run_figure_label_audit


ALLOWED_ABBREVIATIONS = ["DAS", "Rayleigh", "Vp", "Vs", "CFL", "PML", "RMS", "x-y-depth", "gauge length"]


def run_figure_language_check(latest_stable_dir: Path) -> dict[str, Any]:
    """检查图件 metadata 是否声明中文化，并附加 case label 审计结果。"""

    latest = Path(latest_stable_dir)
    manifest_path = latest / "metadata" / "figure_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    english: list[str] = []
    checked = 0
    for item in manifest.get("passed_items", []):
        rel = f"figures/{item.get('category')}/{item.get('filename')}"
        if not (latest / rel).exists():
            continue
        checked += 1
        metadata = item.get("metadata") or {}
        if metadata.get("language") != "zh":
            english.append(rel)
    label_audit = run_figure_label_audit(latest)
    return {
        "stage": "Stage 5G",
        "checked_count": checked,
        "english_figure_count": len(english),
        "english_or_needs_translation": english,
        "allowed_abbreviations": ALLOWED_ABBREVIATIONS,
        "label_audit": label_audit,
        "status": "pass" if not english and label_audit["status"] == "pass" else "warning",
        "note": "未使用 OCR；检查依据为 figure manifest、中文标签映射和绘图函数约定。",
    }


def write_figure_language_report(path: Path, result: dict[str, Any]) -> None:
    """写出图件语言检查报告。"""

    lines = [
        "# 图件语言检查报告",
        "",
        "本报告不使用 OCR，而是检查 latest_stable figure manifest 的 `language=zh` 标记和绘图 case label 映射。",
        "DAS、Rayleigh、Vp、Vs、CFL、PML、RMS、gauge length 等标准缩写允许保留。",
        "",
        f"- 检查图件总数：`{result['checked_count']}`",
        f"- 英文图或需中文化图数量：`{result['english_figure_count']}`",
        f"- 状态：`{result['status']}`",
        f"- 允许缩写：`{result['allowed_abbreviations']}`",
        "",
        "## 需要中文化清单",
        "",
    ]
    lines.extend(f"- `{item}`" for item in result["english_or_needs_translation"] or ["无"])
    lines.extend(append_label_audit_report_lines(result["label_audit"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
