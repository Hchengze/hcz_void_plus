"""Stage 5F latest_stable 图件质量检查。

该模块在文件级 self-check 之外，进一步计算像素方差、边缘强度和非背景比例。
它不理解图件语义，但可以阻止全白、全黑、单色或近似空图进入 current curated
latest_stable。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


def _read_image(path: Path) -> np.ndarray:
    import matplotlib.image as mpimg

    image = np.asarray(mpimg.imread(path), dtype=float)
    if image.ndim == 3:
        image = image[..., :3].mean(axis=2)
    return image


def check_figure_quality(path: Path) -> dict[str, Any]:
    """检查单张图件质量。

    这里的阈值故意保守：科研图通常有坐标轴、文字或色带，即使主体数据较弱，
    像素方差和边缘强度也不应接近零。
    """

    path = Path(path)
    reasons: list[str] = []
    if not path.exists():
        return {"path": str(path), "passed": False, "reasons": ["missing"], "size_bytes": 0}
    size = path.stat().st_size
    if size < 2048:
        reasons.append("file_too_small")
    try:
        image = _read_image(path)
        height, width = image.shape[:2]
        if width < 240 or height < 160:
            reasons.append("resolution_too_low")
        finite = image[np.isfinite(image)]
        if finite.size == 0:
            reasons.append("no_finite_pixels")
            variance = 0.0
            edge_strength = 0.0
            non_background_ratio = 0.0
        else:
            variance = float(np.var(finite))
            gx = np.diff(image, axis=1)
            gz = np.diff(image, axis=0)
            edge_strength = float(np.mean(np.abs(gx))) + float(np.mean(np.abs(gz)))
            median = float(np.median(finite))
            non_background_ratio = float(np.mean(np.abs(finite - median) > 0.01))
            if variance < 1.0e-5:
                reasons.append("low_pixel_variance")
            if edge_strength < 1.0e-4:
                reasons.append("low_edge_strength")
            if non_background_ratio < 0.005:
                reasons.append("too_little_non_background_area")
    except Exception as exc:  # pragma: no cover - 图像库异常跨版本不同
        reasons.append(f"unreadable:{type(exc).__name__}")
        width = height = 0
        variance = edge_strength = non_background_ratio = 0.0
    return {
        "path": str(path),
        "filename": path.name,
        "passed": not reasons,
        "reasons": reasons,
        "size_bytes": size,
        "width_px": int(width),
        "height_px": int(height),
        "pixel_variance": variance,
        "edge_strength": edge_strength,
        "non_background_ratio": non_background_ratio,
    }


def run_figure_quality_check(latest_stable_dir: Path) -> dict[str, Any]:
    """检查 latest_stable 中全部 PNG 图件。"""

    latest = Path(latest_stable_dir)
    figures = sorted((latest / "figures").glob("*/*.png"))
    items = [check_figure_quality(path) for path in figures]
    failed = [item for item in items if not item["passed"]]
    return {
        "stage": "Stage 5G",
        "checked_count": len(items),
        "empty_figure_count": len(failed),
        "excluded_empty_figures": [item["path"] for item in failed],
        "items": items,
        "status": "pass" if not failed else "warning",
    }


def write_figure_quality_report(path: Path, result: dict[str, Any]) -> None:
    """写出图件质量报告。"""

    lines = [
        "# 图件质量检查报告",
        "",
        f"- 检查图件总数：`{result['checked_count']}`",
        f"- 空图/低质量图数量：`{result['empty_figure_count']}`",
        f"- 状态：`{result['status']}`",
        "",
        "## 被排除空图或低质量图",
        "",
    ]
    lines.extend(f"- `{item}`" for item in result["excluded_empty_figures"] or ["无。"])
    lines.extend(["", "## 指标摘要", "", "| figure | variance | edge | non_background | passed |", "|---|---:|---:|---:|---|"])
    for item in result["items"]:
        lines.append(
            f"| `{Path(item['path']).name}` | {item['pixel_variance']:.4g} | "
            f"{item['edge_strength']:.4g} | {item['non_background_ratio']:.4g} | {item['passed']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
