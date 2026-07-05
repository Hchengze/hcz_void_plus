from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.utils.latest_stable_manifest import STAGE5H_FIGURE_SPECS, STAGE5H_ANIMATION_SPECS
from src.utils.stable_export import export_latest_stable_outputs


def _touch(path: Path, text: str = "x"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_valid_png(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    image = np.outer(np.linspace(0.0, 1.0, 80), np.linspace(1.0, 0.0, 120))
    fig, ax = plt.subplots(figsize=(3.2, 2.4), dpi=100)
    ax.imshow(image, cmap="viridis")
    ax.set_title("中文测试图")
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    fig.savefig(path)
    plt.close(fig)


def test_export_latest_stable_outputs_creates_stage5h_three_category_directory(tmp_path):
    run_dir = tmp_path / "stage5h_run_20260705_000000"
    latest = tmp_path / "latest_stable"
    for spec in STAGE5H_FIGURE_SPECS:
        _write_valid_png(run_dir / "figures" / spec.filename)
    for spec in STAGE5H_ANIMATION_SPECS:
        path = run_dir / "animations" / spec.filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"GIF89a" + b"0" * 4096)
    for name in [
        "report_full_pipeline.md",
        "report_velocity_model_visualization.md",
        "report_velocity_model_physics_bridge.md",
        "report_elastic2d_rayleigh_benchmark.md",
        "report_elastic2d_das_response.md",
        "report_model_mismatch.md",
        "report_elastic_vs_kinematic.md",
    ]:
        _touch(run_dir / "reports" / name, "Stage 5G report")
    _touch(run_dir / "metadata" / "meta_run.json", "{}")
    _touch(run_dir / "metadata" / "params_snapshot.json", "{}")

    info = export_latest_stable_outputs(
        run_dir,
        latest,
        {
            "commit_id": "abc1234",
            "algorithm_commit": "abc1234",
            "latest_stable_commit": "generated_from_algorithm_commit",
            "task_name": "pytest",
            "source_run_dir": str(run_dir),
            "active_velocity_model_type": "layered",
            "forward_engine_active": "layered_kinematic",
            "rayleigh_like_event_detected": False,
            "das_gauge_final_status": "nonzero_but_weak_not_for_default_localization",
            "stage5f_validation": {"ready_for_2p5d": False, "elastic2d_rayleigh_benchmark": {}},
            "confidence": {"high_score_region": {}},
        },
    )

    assert latest.exists()
    assert (latest / "README.md").exists()
    assert (latest / "archive_manifest.md").exists()
    assert set(path.name for path in (latest / "figures").iterdir()) == {"forward", "localization", "error_analysis"}
    assert (latest / "figures" / "forward" / "fig_geometry_3d_overview.png").exists()
    assert (latest / "animations" / "forward" / "anim_multishot_forward_overview.gif").exists()
    assert not (latest / "figures" / "unselected_extra.png").exists()
    assert len(list((latest / "figures").glob("*.png"))) == 0
    assert not (latest / "arrays").exists()
    assert (latest / "reports" / "error_analysis" / "report_latest_stable_file_audit.md").exists()
    assert (latest / "reports" / "error_analysis" / "report_latest_stable_tree_snapshot.md").exists()
    assert (latest / "reports" / "error_analysis" / "report_manual_review_readiness.md").exists()
    assert (latest / "reports" / "error_analysis" / "report_figure_quality_check.md").exists()
    assert (latest / "metadata" / "meta_run.json").exists()
    assert (latest / "metadata" / "meta_params_snapshot.json").exists()
    assert (latest / "metadata" / "latest_stable_tree_snapshot.txt").exists()
    summary = (latest / "summary.md").read_text(encoding="utf-8")
    assert "Stage 5H" in summary
    assert "algorithm_commit = `abc1234`" in summary
    assert "latest_stable_commit" in summary
    assert info["copied"]
