"""Stage 2 full_pipeline：正演 + 伪波场 + 基础扫描定位。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

from src.pipeline.run_forward_pipeline import run_forward_pipeline
from src.pipeline.run_scan_pipeline import run_scan_pipeline


def _write_full_pipeline_report(params: SimpleNamespace, output_path: Path, scan_result: dict[str, Any]) -> None:
    """写出综合中文报告。"""

    best = scan_result["best_location"]
    error = scan_result["truth_error"]
    content = f"""# Full Pipeline 综合报告

本次运行完成：DAS-like 运动学多炮正演、中文图件、运动学伪波场快照/GIF、直达波预测、基础 x-y-h 多炮扫描定位。

## 当前近似条件

- forward：`kinematic approximation`
- DAS-like：`DAS-like response approximation`
- velocity：`uniform effective Rayleigh velocity`
- surface response：`kinematic_surface_response_snapshot`，只是 Rayleigh 波走时控制的地表响应示意，不是真实弹性波模拟
- Rayleigh depth sensitivity：`exp(-h / penetration_depth)` 简化权重，不是严格模态深度核

## 扫描结果

- score method：`{params.scan.score_method}`
- score volume shape：`{tuple(scan_result["score_volume"].shape)}`
- scan depth weighting：`{params.scan.use_depth_weight}`
- best_location：x=`{best["x_m"]}` m，y=`{best["y_m"]}` m，h=`{best["depth_m"]}` m
- truth_error distance：`{error["distance_m"]}` m

## 风险提示

单侧 DAS-like 几何下 y-depth 可能耦合。best_location 是运动学局部能量聚焦结果，不能作为工程确诊结论。
"""
    output_path.write_text(content, encoding="utf-8")


def run_full_pipeline(params: SimpleNamespace) -> dict[str, Any]:
    """运行 Stage 2 完整闭环。"""

    forward_result = run_forward_pipeline(params)
    scan_result: dict[str, Any] | None = None
    if params.scan.enabled:
        scan_result = run_scan_pipeline(params, forward_result)
        _write_full_pipeline_report(
            params,
            forward_result["paths"]["reports"] / "report_full_pipeline.md",
            scan_result,
        )
    else:
        (forward_result["paths"]["reports"] / "report_full_pipeline.md").write_text(
            "本次 full_pipeline 关闭了 scan_enabled，因此只完成正演和伪波场输出。\n",
            encoding="utf-8",
        )

    result = dict(forward_result)
    result["scan_result"] = scan_result
    return result
