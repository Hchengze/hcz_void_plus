"""Stage 3 full_pipeline：正演 + 扫描 + 基础置信度 + 稳定成果导出。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from src.confidence.confidence_report import build_confidence_metrics, write_confidence_report
from src.pipeline.run_forward_pipeline import run_forward_pipeline
from src.pipeline.run_scan_pipeline import run_scan_pipeline
from src.utils.metadata import build_metadata, save_json
from src.utils.stable_export import export_latest_stable_outputs, get_git_commit_id
from src.visualization.plot_confidence import plot_confidence_diagnostics


def _write_full_pipeline_report(
    params: SimpleNamespace,
    output_path: Path,
    scan_result: dict[str, Any],
    confidence_metrics: dict[str, Any] | None = None,
) -> None:
    """写出综合中文报告。"""

    best = scan_result["best_location"]
    error = scan_result["truth_error"]
    confidence_text = "本次未执行基础置信度分析。"
    if confidence_metrics is not None:
        peak = confidence_metrics["peak"]
        contrast = confidence_metrics["contrast"]
        consistency = confidence_metrics["multi_shot_consistency"]
        coupling = confidence_metrics["y_depth_coupling"]
        confidence_text = f"""- peak sharpness：`{peak["peak_sharpness"]:.4g}`
- score contrast：`{contrast["score_contrast"]:.4g}`
- score percentile：`{contrast["score_percentile"]:.2f}%`
- multi-shot consistency CV：`{consistency["coefficient_of_variation"]:.4g}`
- y-depth coupling warning：`{coupling["warning"]}`
- confidence flag：`{confidence_metrics["low_confidence_flag"]}`

这些指标只是规则型科研诊断，用于帮助人工判断结果是否稳定，不能作为工程确诊。"""
    content = f"""# Full Pipeline 综合报告

本次运行完成：DAS-like 运动学多炮正演、中文图件、运动学地表响应示意图/GIF、直达波预测、基础 x-y-h 多炮扫描定位和 Stage 3 基础置信度诊断。

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

## 基础置信度分析

{confidence_text}

## 风险提示

单侧 DAS-like 几何下 y-depth 可能耦合。best_location 是运动学局部能量聚焦结果，不能作为工程确诊结论。
"""
    output_path.write_text(content, encoding="utf-8")


def _build_final_metadata(
    params: SimpleNamespace,
    forward_result: dict[str, Any],
    scan_result: dict[str, Any],
    confidence_metrics: dict[str, Any],
    latest_stable_path: Path | None,
    latest_stable_exported: bool,
) -> dict[str, Any]:
    """在 full_pipeline 收尾阶段写出包含置信度和稳定导出状态的 metadata。"""

    paths = forward_result["paths"]
    git_info = {
        "commit_id": get_git_commit_id(Path.cwd()),
        # pipeline 只能记录“本轮预期会 push”的工作流状态；真正 push 成功与否由收尾 git push 命令确认。
        "push_attempted": True,
        "push_success": False,
    }
    output_info = {
        "latest_stable_exported": latest_stable_exported,
        "latest_stable_path": str(latest_stable_path) if latest_stable_path is not None else None,
    }
    metadata = build_metadata(
        params,
        forward_result["synthetic_data"],
        forward_result["scatter_xyz"],
        forward_result["scatter_weight"],
        font_info=forward_result.get("font_info", {}),
        wavefield_info=forward_result.get("wavefield_info", {}),
        scan_result=scan_result,
        diagnostics_info={
            "diffraction_travel_time_curve_figure": str(paths["figures"] / "fig_diffraction_travel_time_curves.png"),
            "path_section_figure": str(paths["figures"] / "fig_source_anomaly_receiver_path_section.png"),
            "depth_sensitivity_figure": str(paths["figures"] / "fig_rayleigh_depth_sensitivity.png"),
        },
        confidence_info=confidence_metrics,
        output_info=output_info,
        git_info=git_info,
    )
    save_json(paths["metadata"] / "meta_run.json", metadata)
    return metadata


def run_full_pipeline(params: SimpleNamespace) -> dict[str, Any]:
    """运行 Stage 3 完整闭环。

    流程顺序：
        1. 运动学 DAS-like 正演；
        2. x-y-h 多炮扫描定位；
        3. 基础置信度诊断；
        4. 综合报告和 metadata；
        5. 可选导出 outputs/latest_stable 精选成果。
    """

    forward_result = run_forward_pipeline(params)
    scan_result: dict[str, Any] | None = None
    confidence_metrics: dict[str, Any] | None = None
    stable_export_info: dict[str, Any] | None = None
    if params.scan.enabled:
        scan_result = run_scan_pipeline(params, forward_result)
        paths = forward_result["paths"]
        confidence_metrics = build_confidence_metrics(
            params,
            scan_result,
            scan_result["scan_data"],
            params.derived.time_axis,
            forward_result["source_xyz"],
            forward_result["receiver_xyz"],
            forward_result["velocity_model"],
        )
        if params.output.save_arrays:
            save_json(paths["arrays"] / "arr_confidence_metrics.json", confidence_metrics)
        if params.output.save_figures:
            plot_confidence_diagnostics(
                params,
                scan_result,
                confidence_metrics,
                paths["figures"] / "fig_confidence_diagnostics.png",
            )
        if params.output.save_report:
            write_confidence_report(params, paths["reports"] / "report_confidence.md", confidence_metrics)
        _write_full_pipeline_report(
            params,
            forward_result["paths"]["reports"] / "report_full_pipeline.md",
            scan_result,
            confidence_metrics,
        )
        latest_stable_path = Path(params.derived.latest_stable_dir)
        _build_final_metadata(
            params,
            forward_result,
            scan_result,
            confidence_metrics,
            latest_stable_path if params.output.export_latest_stable else None,
            bool(params.output.export_latest_stable),
        )
        if params.output.export_latest_stable:
            summary_info = {
                "commit_id": get_git_commit_id(Path.cwd()),
                "task_name": "Stage 3 基础置信度指标 + 稳定成果输出管理",
                "run_time": datetime.now().isoformat(timespec="seconds"),
                "source_run_dir": str(forward_result["paths"]["root"]),
                "best_location": scan_result["best_location"],
                "truth_error": scan_result["truth_error"],
                "confidence": confidence_metrics,
            }
            stable_export_info = export_latest_stable_outputs(
                forward_result["paths"]["root"],
                latest_stable_path,
                summary_info,
            )
    else:
        (forward_result["paths"]["reports"] / "report_full_pipeline.md").write_text(
            "本次 full_pipeline 关闭了 scan_enabled，因此只完成正演和伪波场输出。\n",
            encoding="utf-8",
        )

    result = dict(forward_result)
    result["scan_result"] = scan_result
    result["confidence_metrics"] = confidence_metrics
    result["stable_export_info"] = stable_export_info
    return result
