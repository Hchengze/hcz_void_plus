"""Stage 5F latest_stable 图件重复检查。"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np


def _read_gray(path: Path) -> np.ndarray:
    import matplotlib.image as mpimg

    image = np.asarray(mpimg.imread(path), dtype=float)
    if image.ndim == 3:
        image = image[..., :3].mean(axis=2)
    return image


def _average_hash(path: Path, bins: int = 8) -> str:
    """生成简化 average hash，用于发现明显重复图。"""

    image = _read_gray(path)
    ys = np.linspace(0, image.shape[0], bins + 1, dtype=int)
    xs = np.linspace(0, image.shape[1], bins + 1, dtype=int)
    pooled = np.zeros((bins, bins), dtype=float)
    for iy in range(bins):
        for ix in range(bins):
            block = image[ys[iy] : ys[iy + 1], xs[ix] : xs[ix + 1]]
            pooled[iy, ix] = float(np.mean(block)) if block.size else 0.0
    return "".join("1" if value > float(np.mean(pooled)) else "0" for value in pooled.ravel())


def _hamming(a: str, b: str) -> int:
    return sum(ch1 != ch2 for ch1, ch2 in zip(a, b))


def run_figure_deduplication(latest_stable_dir: Path) -> dict[str, Any]:
    """检测 latest_stable 中的文件名重复、字节重复和感知近似重复。"""

    latest = Path(latest_stable_dir)
    figures = sorted((latest / "figures").glob("*/*.png"))
    seen_names: dict[str, str] = {}
    seen_sha: dict[str, str] = {}
    hashes: dict[str, str] = {}
    shapes: dict[str, tuple[int, int]] = {}
    duplicate_items: list[dict[str, str]] = []
    for path in figures:
        rel = path.relative_to(latest).as_posix()
        if path.name in seen_names:
            duplicate_items.append({"kind": "filename", "kept": seen_names[path.name], "duplicate": rel})
        else:
            seen_names[path.name] = rel
        sha = hashlib.sha1(path.read_bytes()).hexdigest()
        if sha in seen_sha:
            duplicate_items.append({"kind": "sha1", "kept": seen_sha[sha], "duplicate": rel})
        else:
            seen_sha[sha] = rel
        gray = _read_gray(path)
        shapes[rel] = tuple(int(v) for v in gray.shape[:2])
        hashes[rel] = _average_hash(path)
    rels = list(hashes)
    for i, rel_a in enumerate(rels):
        for rel_b in rels[i + 1 :]:
            if shapes[rel_a] == shapes[rel_b] and _hamming(hashes[rel_a], hashes[rel_b]) == 0:
                duplicate_items.append({"kind": "perceptual", "kept": rel_a, "duplicate": rel_b})
    return {
        "stage": "Stage 5G",
        "checked_count": len(figures),
        "duplicate_figure_count": len(duplicate_items),
        "excluded_duplicate_figures": duplicate_items,
        "status": "pass" if not duplicate_items else "warning",
    }


def write_figure_deduplication_report(path: Path, result: dict[str, Any]) -> None:
    """写出重复图检查报告。"""

    lines = [
        "# 图件重复检查报告",
        "",
        f"- 检查图件总数：`{result['checked_count']}`",
        f"- 重复图数量：`{result['duplicate_figure_count']}`",
        f"- 状态：`{result['status']}`",
        "",
        "## 重复图清单",
        "",
    ]
    if not result["excluded_duplicate_figures"]:
        lines.append("- 无。")
    else:
        for item in result["excluded_duplicate_figures"]:
            lines.append(f"- `{item['kind']}`：保留 `{item['kept']}`，排除 `{item['duplicate']}`")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
