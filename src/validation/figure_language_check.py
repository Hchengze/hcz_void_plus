"""Stage 5F latest_stable 图件语言检查。

当前不引入 OCR。语言检查基于 curated manifest 和绘图函数约定：每张进入
latest_stable 的图件必须在 metadata 中标注 `language=zh`。标准缩写 DAS、
Rayleigh、Vp、Vs、CFL、PML、RMS 允许保留。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ALLOWED_ABBREVIATIONS = ["DAS", "Rayleigh", "Vp", "Vs", "CFL", "PML", "RMS", "x-y-depth"]


def run_figure_language_check(latest_stable_dir: Path) -> dict[str, Any]:
    """检查图件 metadata 是否声明中文化。"""

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
    return {
        "stage": "Stage 5F",
        "checked_count": checked,
        "english_figure_count": len(english),
        "english_or_needs_translation": english,
        "allowed_abbreviations": ALLOWED_ABBREVIATIONS,
        "status": "pass" if not english else "warning",
        "note": "未使用 OCR；检查依据为绘图清单 metadata 与人工可审计绘图函数。",
    }


def write_figure_language_report(path: Path, result: dict[str, Any]) -> None:
    """写出图件语言检查报告。"""

    lines = [
        "# 图件语言检查报告",
        "",
        "本报告不使用 OCR，而是检查 latest_stable figure manifest 的 `language=zh` 标记。",
        "DAS、Rayleigh、Vp、Vs、CFL、PML、RMS 等标准缩写允许保留。",
        "",
        f"- 检查图件总数：`{result['checked_count']}`",
        f"- 英文图或需中文化图数量：`{result['english_figure_count']}`",
        f"- 状态：`{result['status']}`",
        f"- 允许缩写：`{result['allowed_abbreviations']}`",
        "",
        "## 需中文化清单",
        "",
    ]
    lines.extend(f"- `{item}`" for item in result["english_or_needs_translation"] or ["无。"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
