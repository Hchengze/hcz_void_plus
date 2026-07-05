"""latest_stable 图件自检。

Stage 5D 要求“图件不能只生成出来就进入 latest_stable”。本模块在导出前检查
候选图像：文件是否存在、能否读取、是否近似空白、分辨率是否足够、类别是否
正确，以及 manifest 元数据是否指向当前阶段/当前 forward/当前速度模型。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from src.utils.latest_stable_manifest import StableFigureSpec, expected_category_for_filename


def _read_image(path: Path) -> np.ndarray:
    """读取图像像素。

    优先使用 matplotlib.image.imread，避免新增 Pillow 依赖。若图像不可读，调用方会
    捕获异常并将其记为 failed，而不是让 full_pipeline 中断在图件导出阶段。
    """

    import matplotlib.image as mpimg

    return np.asarray(mpimg.imread(path), dtype=float)


def check_single_figure(
    path: Path,
    *,
    expected_category: str,
    metadata: dict[str, Any],
    min_size_bytes: int = 1024,
    min_width_px: int = 120,
    min_height_px: int = 90,
) -> dict[str, Any]:
    """检查单张图是否适合进入 latest_stable。

    返回字典而不是抛异常，是为了让报告列出所有失败原因；这样旧图、重复图或
    空白图不会悄悄进入精选目录。
    """

    reasons: list[str] = []
    if not path.exists():
        return {
            "filename": path.name,
            "path": str(path),
            "category": expected_category,
            "passed": False,
            "reasons": ["missing_file"],
            "size_bytes": 0,
        }

    size_bytes = path.stat().st_size
    if size_bytes < min_size_bytes:
        reasons.append("file_too_small")

    width = 0
    height = 0
    dynamic_range = 0.0
    try:
        image = _read_image(path)
        if image.ndim < 2:
            reasons.append("not_2d_image")
        else:
            height, width = int(image.shape[0]), int(image.shape[1])
            if width < min_width_px or height < min_height_px:
                reasons.append("resolution_too_low")
            finite = image[np.isfinite(image)]
            if finite.size == 0:
                reasons.append("no_finite_pixels")
            else:
                dynamic_range = float(np.nanmax(finite) - np.nanmin(finite))
                std = float(np.nanstd(finite))
                if dynamic_range < 1.0e-6 or std < 1.0e-6:
                    reasons.append("near_blank_image")
    except Exception as exc:  # pragma: no cover - 具体图像库错误类型跨版本不同
        reasons.append(f"unreadable_image:{type(exc).__name__}")

    expected_from_name = expected_category_for_filename(path.name)
    if expected_from_name != expected_category:
        reasons.append(f"category_mismatch:{expected_from_name}")

    for key in ["stage", "forward_engine", "velocity_model_type", "category"]:
        if key not in metadata:
            reasons.append(f"missing_metadata:{key}")
    if metadata.get("category") != expected_category:
        reasons.append("metadata_category_mismatch")
    if "Stage 3" in str(metadata.get("stage")) or "Stage 4" in str(metadata.get("stage")):
        reasons.append("old_stage_metadata")

    return {
        "filename": path.name,
        "path": str(path),
        "category": expected_category,
        "passed": len(reasons) == 0,
        "reasons": reasons,
        "size_bytes": size_bytes,
        "width_px": width,
        "height_px": height,
        "dynamic_range": dynamic_range,
        "metadata": metadata,
    }


def run_figure_self_check(
    run_output_dir: Path,
    figure_specs: list[StableFigureSpec],
    figure_metadata: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """对全部精选候选图执行自检。"""

    run_output_dir = Path(run_output_dir)
    seen: set[tuple[str, str]] = set()
    items: list[dict[str, Any]] = []
    duplicate_files: list[str] = []
    for spec in figure_specs:
        key = (spec.category, spec.filename)
        if key in seen:
            duplicate_files.append(f"{spec.category}/{spec.filename}")
            continue
        seen.add(key)
        metadata = figure_metadata.get(spec.filename, {})
        items.append(
            check_single_figure(
                run_output_dir / "figures" / spec.filename,
                expected_category=spec.category,
                metadata=metadata,
            )
        )

    passed = [item for item in items if item["passed"]]
    failed = [item for item in items if not item["passed"]]
    excluded_old = [
        item["filename"]
        for item in failed
        if any("old_stage" in reason for reason in item.get("reasons", []))
    ]
    missing_metadata = [
        item["filename"]
        for item in failed
        if any("missing_metadata" in reason for reason in item.get("reasons", []))
    ]
    return {
        "stage": "Stage 5H",
        "checked_count": len(items),
        "passed_count": len(passed),
        "failed_count": len(failed),
        "items": items,
        "passed_items": passed,
        "failed_items": failed,
        "excluded_old_figures": excluded_old,
        "excluded_duplicate_figures": duplicate_files,
        "missing_metadata_figures": missing_metadata,
        "status": "pass" if not failed and not duplicate_files else "warning",
        "recommended_figures": [f"{item['category']}/{item['filename']}" for item in passed],
    }


def write_figure_self_check_report(path: Path, result: dict[str, Any]) -> None:
    """写出图件自检报告。"""

    lines = [
        "# 图件自检报告",
        "",
        "本报告由 Stage 5H 在 latest_stable 导出前生成。只有通过自检的精选图件会进入 latest_stable；",
        "未通过的图仍保留在时间戳运行目录中，供调试追溯。",
        "",
        f"- 检查图件总数：`{result['checked_count']}`",
        f"- 通过数量：`{result['passed_count']}`",
        f"- 失败数量：`{result['failed_count']}`",
        f"- 状态：`{result['status']}`",
        f"- 被排除旧图：`{result['excluded_old_figures']}`",
        f"- 被排除重复图：`{result['excluded_duplicate_figures']}`",
        f"- 缺失 metadata 图：`{result['missing_metadata_figures']}`",
        "",
        "## 失败明细",
        "",
    ]
    if not result["failed_items"]:
        lines.append("- 无。")
    else:
        for item in result["failed_items"]:
            lines.append(f"- `{item['category']}/{item['filename']}`：{item['reasons']}")
    lines.extend(["", "## 推荐人工查看图件", ""])
    lines.extend(f"- `{name}`" for name in result["recommended_figures"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
