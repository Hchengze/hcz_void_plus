"""导出 Stage 5H latest_stable 三类精选成果。"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from src.utils.latest_stable_curator import (
    audit_latest_stable_files,
    build_latest_stable_tree_snapshot,
    write_latest_stable_file_audit_report,
    write_latest_stable_tree_snapshot,
    write_latest_stable_tree_snapshot_report,
)
from src.utils.latest_stable_manifest import (
    STAGE5H_ANIMATION_SPECS,
    STAGE5H_FIGURE_SPECS,
    animation_specs_by_category,
    build_figure_metadata,
    specs_by_category,
)
from src.validation.figure_deduplication import run_figure_deduplication, write_figure_deduplication_report
from src.validation.figure_language_check import run_figure_language_check, write_figure_language_report
from src.validation.figure_quality_check import run_figure_quality_check, write_figure_quality_report
from src.validation.figure_self_check import run_figure_self_check, write_figure_self_check_report
from src.validation.manual_review_readiness import (
    run_manual_review_readiness,
    write_manual_review_readiness_report,
)


LATEST_STABLE_CATEGORIES = ["forward", "localization", "error_analysis"]
CURATED_FIGURES = specs_by_category()
CURATED_ANIMATIONS = animation_specs_by_category()

CURATED_REPORTS = {
    "forward": [
        "report_full_pipeline.md",
        "report_velocity_model_visualization.md",
        "report_velocity_model_physics_bridge.md",
        "report_elastic2d_rayleigh_benchmark.md",
        "report_elastic2d_das_response.md",
    ],
    "localization": [
        "report_full_pipeline.md",
    ],
    "error_analysis": [
        "report_figure_quality_check.md",
        "report_figure_deduplication.md",
        "report_figure_language_check.md",
        "report_latest_stable_file_audit.md",
        "report_latest_stable_tree_snapshot.md",
        "report_manual_review_readiness.md",
    ],
}

MANUAL_REVIEW_FIGURES = [
    "figures/forward/fig_geometry_3d_overview.png",
    "figures/forward/fig_velocity_model_active_badge.png",
    "figures/forward/fig_velocity_model_physics_bridge.png",
    "figures/forward/fig_elastic2d_rayleigh_benchmark_matrix.png",
    "figures/forward/fig_elastic2d_rayleigh_velocity_error.png",
    "figures/forward/fig_elastic2d_das_best_case.png",
    "figures/localization/fig_3d_high_score_region.png",
    "figures/localization/fig_recommended_location_3d.png",
    "figures/localization/fig_3d_uncertainty_box.png",
    "figures/error_analysis/fig_stage5h_status_badge.png",
]

MANUAL_REVIEW_ANIMATIONS = [
    "animations/forward/anim_multishot_forward_overview.gif",
    "animations/forward/anim_single_shot_wavefield.gif",
]

LEGACY_STABLE_FILES = [
    "acoustic2d shot gather 与 acoustic2d wavefield snapshots：F2 基础设施验证，不再占据当前主视图。",
    "forward_engine_comparison 与 layered_kinematic_vs_baseline_gather：转为历史诊断，不再进入 Stage 5H 精选。",
    "Stage 5E sensitivity/pick 旧图：由 Stage 5H Rayleigh benchmark 矩阵和速度误差图替代。",
    "重复 confidence/uncertainty 图：仅保留能说明三维不确定性的 1-2 张。",
    "旧 core/diagnostics/uncertainty/reference_only 细分类目录：合并为 forward/localization/error_analysis 三类。",
]


def get_git_commit_id(repo_root: Path) -> str:
    """读取当前 Git HEAD 短哈希。"""

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


def _reset_latest_stable_dir(latest_stable_dir: Path, output_root_dir: Path) -> None:
    """安全重建 latest_stable 三类目录。"""

    root = output_root_dir.resolve()
    target = latest_stable_dir.resolve()
    if root != target and root not in target.parents:
        raise ValueError(f"拒绝清理 output_root_dir 之外的目录：{target}")
    if latest_stable_dir.exists():
        shutil.rmtree(latest_stable_dir)
    for group in ["figures", "animations", "reports"]:
        for category in LATEST_STABLE_CATEGORIES:
            (latest_stable_dir / group / category).mkdir(parents=True, exist_ok=True)
    (latest_stable_dir / "metadata").mkdir(parents=True, exist_ok=True)


def _copy_if_exists(src: Path, dst: Path, copied: list[str], missing: list[str]) -> None:
    """复制存在的精选文件；缺失时记录但不中断主流程。"""

    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(str(dst))
    else:
        missing.append(str(src))


def _to_builtin(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return {key: _to_builtin(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_builtin(item) for item in value]
    if hasattr(value, "tolist"):
        return value.tolist()
    if hasattr(value, "item"):
        try:
            return value.item()
        except ValueError:
            return value
    return value


def _fmt(value: Any) -> str:
    return "无" if value is None else str(_to_builtin(value))


def _write_latest_stable_readme(path: Path) -> None:
    lines = [
        "# latest_stable",
        "",
        "Stage 5H 继续执行三类精选治理：本目录只保留当前人工复查最需要、且 metadata 可审计的成果。",
        "",
        "## 三类结果",
        "",
        "- `forward/`：正演、速度模型、三维几何、Rayleigh benchmark、DAS-like response 与正演动图。",
        "- `localization/`：x-y-depth 定位、高分候选体、推荐位置和三维不确定性。",
        "- `error_analysis/`：质量检查、误差分析、Rayleigh/DAS 限制和 ready_for_2p5d 判断。",
        "",
        "当前结果是科研候选区，不是工程确诊。2D elastic 只服务三维道路 DAS-like 场景的局部物理验证；三维图件表达几何与定位，不代表 elastic2d 已是三维弹性正演。",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_archive_manifest(path: Path) -> None:
    lines = [
        "# archive manifest",
        "",
        "Stage 5H 不再把历史图件堆进 latest_stable 当前精选目录。",
        "",
        "## 已移出当前精选视图的内容",
        "",
    ]
    lines.extend(f"- {item}" for item in LEGACY_STABLE_FILES)
    lines.extend(
        [
            "",
            "完整历史输出仍可从时间戳运行目录或 Git 历史追溯；latest_stable 只表达当前最稳定结论。",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _manual_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _update_latest_meta_run(path: Path, summary_info: dict[str, Any]) -> None:
    """补写 latest_stable metadata 的 Stage 5H 审计字段。

    时间戳运行目录中的 meta_run.json 记录的是算法运行时刻；导出到 latest_stable
    后需要额外记录本轮稳定输出的来源提交、上一轮稳定提交和当前阶段，方便人工
    复查时不再只看到旧的单一 commit id。
    """

    if not path.exists():
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        payload = {}
    payload["stage"] = "Stage 5H metadata/manual-review hardening"
    payload["previous_stage"] = "Stage 5G"
    payload["algorithm_commit"] = summary_info.get("algorithm_commit")
    payload["latest_stable_commit"] = summary_info.get("latest_stable_commit")
    payload["previous_latest_stable_commit"] = summary_info.get("previous_latest_stable_commit")
    payload["source_run_dir"] = summary_info.get("source_run_dir")
    payload["generated_time"] = summary_info.get("generated_time")
    payload["ready_for_2p5d"] = False
    payload["stage5h_validation"] = {
        "metadata_consistency": True,
        "tree_snapshot_required": True,
        "manual_review_readiness_required": True,
        "ready_for_2p5d": False,
    }
    path.write_text(json.dumps(_to_builtin(payload), ensure_ascii=False, indent=2), encoding="utf-8")


def _write_summary(summary_path: Path, summary_info: dict[str, Any], copied: list[str], missing: list[str]) -> None:
    best = summary_info.get("best_location") or {}
    truth_error = summary_info.get("truth_error") or {}
    confidence = summary_info.get("confidence") or {}
    high_region = confidence.get("high_score_region", {})
    stage5f_validation = summary_info.get("stage5f_validation") or {}
    rayleigh_benchmark = stage5f_validation.get("elastic2d_rayleigh_benchmark") or {}
    latest_audit = summary_info.get("latest_stable_file_audit") or {}
    quality = summary_info.get("figure_quality_check") or {}
    dedup = summary_info.get("figure_deduplication") or {}
    language = summary_info.get("figure_language_check") or {}
    label_audit = summary_info.get("figure_label_audit") or {}
    tree_snapshot = summary_info.get("latest_stable_tree_snapshot") or {}
    manual_review = summary_info.get("manual_review_readiness") or {}
    das_status = summary_info.get("das_gauge_final_status") or stage5f_validation.get("das_gauge_final_status")
    ready_for_2p5d = bool(stage5f_validation.get("ready_for_2p5d", False))
    algorithm_commit = summary_info.get("algorithm_commit") or summary_info.get("commit_id", "unknown")
    latest_stable_commit = summary_info.get("latest_stable_commit", "generated_from_algorithm_commit")
    content = f"""# latest_stable Stage 5H 摘要

## 当前阶段

- stage = Stage 5H
- previous_stage = Stage 5G
- algorithm_commit = `{algorithm_commit}`
- latest_stable_commit = `{latest_stable_commit}`
- previous_latest_stable_commit = `{summary_info.get("previous_latest_stable_commit", "4a7eeb1")}`
- source_run_dir = `{summary_info.get("source_run_dir", "unknown")}`
- generated_time = `{summary_info.get("generated_time", summary_info.get("run_time", datetime.now().isoformat(timespec="seconds")))}`
- 任务名称：`{summary_info.get("task_name", "Stage 5H")}`
- active_velocity_model = `{summary_info.get("active_velocity_model_type", "layered")}`
- active_forward_engine = `{summary_info.get("forward_engine_active", "layered_kinematic")}`
- validation_forward = `elastic2d/staggered`
- ready_for_2p5d = `{ready_for_2p5d}`

## 三类精选结果

- forward 图件数：`{(latest_audit.get("figure_counts") or {}).get("forward")}`
- localization 图件数：`{(latest_audit.get("figure_counts") or {}).get("localization")}`
- error_analysis 图件数：`{(latest_audit.get("figure_counts") or {}).get("error_analysis")}`
- 静态图总数：`{latest_audit.get("latest_stable_total_figure_count")}`
- 动图总数：`{latest_audit.get("latest_stable_total_animation_count")}`
- 报告总数：`{latest_audit.get("latest_stable_total_report_count")}`
- latest_stable_tree_snapshot_status：`{_fmt(tree_snapshot.get("status"))}`
- manual_review_readiness_status：`{_fmt(manual_review.get("status"))}`

## 三维定位结论

- recommended/best location：x=`{_fmt(best.get("x_m"))}` m, y=`{_fmt(best.get("y_m"))}` m, depth=`{_fmt(best.get("depth_m"))}` m
- truth_error：`{_fmt(truth_error.get("distance_m"))}` m
- 3D high-score span：x=`{_fmt(high_region.get("x_span_m"))}` m, y=`{_fmt(high_region.get("y_span_m"))}` m, depth=`{_fmt(high_region.get("depth_span_m"))}` m
- high-score point count：`{_fmt(high_region.get("high_score_region_point_count"))}`

## Rayleigh 与 DAS 状态

- best_rayleigh_benchmark_case：`{_fmt(rayleigh_benchmark.get("best_case"))}`
- rayleigh_like_event_detected：`{_fmt(rayleigh_benchmark.get("rayleigh_like_event_detected"))}`
- rayleigh_velocity_relative_error：`{_fmt(rayleigh_benchmark.get("rayleigh_velocity_relative_error"))}`
- picked_event_interpretation：`{_fmt(rayleigh_benchmark.get("picked_event_interpretation"))}`
- likely_surface_wave_score：`{_fmt(rayleigh_benchmark.get("likely_surface_wave_score"))}`
- likely_boundary_reflection_score：`{_fmt(rayleigh_benchmark.get("likely_boundary_reflection_score"))}`
- likely_body_wave_score：`{_fmt(rayleigh_benchmark.get("likely_body_wave_score"))}`
- late_coda_score：`{_fmt(rayleigh_benchmark.get("late_coda_score"))}`
- failure_reason_ranked：`{_fmt(rayleigh_benchmark.get("failure_reason_ranked"))}`
- das_gauge_final_status：`{_fmt(das_status)}`
- das_best_velocity_gauge_rms：`{_fmt(summary_info.get("das_best_velocity_gauge_rms"))}`
- DAS gauge 默认定位使用：`False`

## 图件质量与中文化

- figure_quality_check_status：`{_fmt(quality.get("status"))}`
- empty_figure_count：`{_fmt(quality.get("empty_figure_count"))}`
- figure_deduplication_status：`{_fmt(dedup.get("status"))}`
- duplicate_figure_count：`{_fmt(dedup.get("duplicate_figure_count"))}`
- figure_language_check_status：`{_fmt(language.get("status"))}`
- english_figure_count：`{_fmt(language.get("english_figure_count"))}`
- figure_label_audit_status：`{_fmt(label_audit.get("status"))}`
- english_case_label_count：`{_fmt(label_audit.get("english_case_label_count"))}`

## 人工复查准备度

- manual_review_figure_count：`{_fmt(manual_review.get("manual_review_figure_count"))}`
- manual_review_animation_count：`{_fmt(manual_review.get("manual_review_animation_count"))}`
- required_3d_figures_present：`{_fmt(manual_review.get("required_3d_figures_present"))}`
- required_animations_present：`{_fmt(manual_review.get("required_animations_present"))}`

## manual_review_figures

{_manual_list(MANUAL_REVIEW_FIGURES)}

## manual_review_animations

{_manual_list(MANUAL_REVIEW_ANIMATIONS)}

## 当前限制

- `layered_kinematic` 仍是当前主定位 forward，属于 straight-ray kinematic approximation。
- `elastic2d/staggered` 仍是 validation forward，不是工业级模拟。
- Rayleigh benchmark 未通过前，`ready_for_2p5d` 必须为 False。
- DAS-like gauge strain 非零但弱且未校准，不默认用于定位，也不等同真实 DAS 仪器响应。
- 2D elastic 只服务三维道路 DAS-like 场景的局部物理验证，不能替代 `source_xyz / receiver_xyz / candidate_xyz` 和 x-y-depth 三维定位。

## 导出记录

- copied：`{len(copied)}`
- missing：`{len(missing)}`
"""
    summary_path.write_text(content, encoding="utf-8")


def export_latest_stable_outputs(
    run_output_dir: Path,
    latest_stable_dir: Path,
    summary_info: dict[str, Any],
) -> dict[str, Any]:
    """导出 Stage 5H 三类 latest_stable 精选成果。"""

    run_output_dir = Path(run_output_dir)
    latest_stable_dir = Path(latest_stable_dir)
    summary_info = dict(summary_info)
    summary_info.setdefault("algorithm_commit", summary_info.get("commit_id", get_git_commit_id(Path.cwd())))
    summary_info.setdefault("latest_stable_commit", "generated_from_algorithm_commit")
    summary_info.setdefault("previous_latest_stable_commit", "4a7eeb1")
    summary_info.setdefault("previous_stage", "Stage 5G")
    summary_info.setdefault("generated_time", datetime.now().isoformat(timespec="seconds"))
    figure_metadata = build_figure_metadata(
        stage="Stage 5H",
        forward_engine=str(summary_info.get("forward_engine_active", "layered_kinematic")),
        velocity_model_type=str(summary_info.get("active_velocity_model_type", "layered")),
    )
    figure_self_check = run_figure_self_check(run_output_dir, STAGE5H_FIGURE_SPECS, figure_metadata)
    write_figure_self_check_report(run_output_dir / "reports" / "report_figure_self_check.md", figure_self_check)
    passed_by_category: dict[str, set[str]] = {}
    for item in figure_self_check["passed_items"]:
        passed_by_category.setdefault(item["category"], set()).add(item["filename"])

    _reset_latest_stable_dir(latest_stable_dir, latest_stable_dir.parent)
    copied: list[str] = []
    missing: list[str] = []

    for category, filenames in CURATED_FIGURES.items():
        for filename in filenames:
            if filename not in passed_by_category.get(category, set()):
                missing.append(str(run_output_dir / "figures" / filename))
                continue
            _copy_if_exists(run_output_dir / "figures" / filename, latest_stable_dir / "figures" / category / filename, copied, missing)

    for category, filenames in CURATED_ANIMATIONS.items():
        for filename in filenames:
            _copy_if_exists(run_output_dir / "animations" / filename, latest_stable_dir / "animations" / category / filename, copied, missing)

    for category, filenames in CURATED_REPORTS.items():
        for filename in filenames:
            if category == "error_analysis" and filename.startswith("report_figure_"):
                continue
            if category == "error_analysis" and filename in {
                "report_latest_stable_file_audit.md",
                "report_latest_stable_tree_snapshot.md",
                "report_manual_review_readiness.md",
            }:
                continue
            _copy_if_exists(run_output_dir / "reports" / filename, latest_stable_dir / "reports" / category / filename, copied, missing)

    _copy_if_exists(run_output_dir / "metadata" / "meta_run.json", latest_stable_dir / "metadata" / "meta_run.json", copied, missing)
    _update_latest_meta_run(latest_stable_dir / "metadata" / "meta_run.json", summary_info)
    _copy_if_exists(
        run_output_dir / "metadata" / "params_snapshot.json",
        latest_stable_dir / "metadata" / "meta_params_snapshot.json",
        copied,
        missing,
    )

    manifest = {
        **figure_self_check,
        "animation_specs": [spec.__dict__ for spec in STAGE5H_ANIMATION_SPECS],
    }
    manifest_path = latest_stable_dir / "metadata" / "figure_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    copied.append(str(manifest_path))

    summary_info["figure_self_check"] = {
        "checked_count": figure_self_check["checked_count"],
        "passed_count": figure_self_check["passed_count"],
        "failed_count": figure_self_check["failed_count"],
        "status": figure_self_check["status"],
    }
    _write_latest_stable_readme(latest_stable_dir / "README.md")
    copied.append(str(latest_stable_dir / "README.md"))
    _write_archive_manifest(latest_stable_dir / "archive_manifest.md")
    copied.append(str(latest_stable_dir / "archive_manifest.md"))

    # 先写基础 summary，供后续质量审计读取。
    _write_summary(latest_stable_dir / "summary.md", summary_info, copied, missing)
    copied.append(str(latest_stable_dir / "summary.md"))

    quality = run_figure_quality_check(latest_stable_dir)
    quality_path = latest_stable_dir / "reports" / "error_analysis" / "report_figure_quality_check.md"
    write_figure_quality_report(quality_path, quality)
    copied.append(str(quality_path))

    dedup = run_figure_deduplication(latest_stable_dir)
    dedup_path = latest_stable_dir / "reports" / "error_analysis" / "report_figure_deduplication.md"
    write_figure_deduplication_report(dedup_path, dedup)
    copied.append(str(dedup_path))

    language = run_figure_language_check(latest_stable_dir)
    language_path = latest_stable_dir / "reports" / "error_analysis" / "report_figure_language_check.md"
    write_figure_language_report(language_path, language)
    copied.append(str(language_path))

    latest_audit = audit_latest_stable_files(latest_stable_dir)
    audit_path = latest_stable_dir / "reports" / "error_analysis" / "report_latest_stable_file_audit.md"
    write_latest_stable_file_audit_report(audit_path, latest_audit)
    copied.append(str(audit_path))
    latest_audit = audit_latest_stable_files(latest_stable_dir)
    write_latest_stable_file_audit_report(audit_path, latest_audit)

    tree_snapshot = build_latest_stable_tree_snapshot(latest_stable_dir)
    tree_snapshot_path = latest_stable_dir / "metadata" / "latest_stable_tree_snapshot.txt"
    write_latest_stable_tree_snapshot(tree_snapshot_path, tree_snapshot)
    copied.append(str(tree_snapshot_path))
    tree_report_path = latest_stable_dir / "reports" / "error_analysis" / "report_latest_stable_tree_snapshot.md"
    write_latest_stable_tree_snapshot_report(tree_report_path, tree_snapshot)
    copied.append(str(tree_report_path))

    summary_info["figure_quality_check"] = {
        "status": quality["status"],
        "empty_figure_count": quality["empty_figure_count"],
    }
    summary_info["figure_deduplication"] = {
        "status": dedup["status"],
        "duplicate_figure_count": dedup["duplicate_figure_count"],
    }
    summary_info["figure_language_check"] = {
        "status": language["status"],
        "english_figure_count": language["english_figure_count"],
    }
    summary_info["figure_label_audit"] = language.get("label_audit", {})
    summary_info["latest_stable_file_audit"] = latest_audit
    summary_info["latest_stable_tree_snapshot"] = tree_snapshot
    # 先写入带 tree snapshot 的 summary，再运行 manual review readiness，
    # 因为 readiness 需要读取 summary 中的人工复查清单。
    _write_summary(latest_stable_dir / "summary.md", summary_info, copied, missing)
    manual_review = run_manual_review_readiness(latest_stable_dir)
    manual_review_path = latest_stable_dir / "reports" / "error_analysis" / "report_manual_review_readiness.md"
    write_manual_review_readiness_report(manual_review_path, manual_review)
    copied.append(str(manual_review_path))
    summary_info["manual_review_readiness"] = manual_review
    _write_summary(latest_stable_dir / "summary.md", summary_info, copied, missing)

    return {
        "latest_stable_dir": str(latest_stable_dir),
        "copied": copied,
        "missing": missing,
        "summary_path": str(latest_stable_dir / "summary.md"),
    }
