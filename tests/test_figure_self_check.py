from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.utils.latest_stable_manifest import StableFigureSpec, build_figure_metadata
from src.validation.figure_self_check import check_single_figure, run_figure_self_check


def _write_nonblank_png(path: Path) -> None:
    data = np.outer(np.linspace(0.0, 1.0, 32), np.linspace(0.0, 1.0, 48))
    fig, ax = plt.subplots(figsize=(3, 2))
    ax.imshow(data, cmap="viridis")
    ax.set_axis_off()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=100)
    plt.close(fig)


def test_single_figure_self_check_passes_nonblank_current_stage(tmp_path):
    path = tmp_path / "figures" / "fig_velocity_model_active_badge.png"
    _write_nonblank_png(path)
    metadata = build_figure_metadata(
        stage="Stage 5D",
        forward_engine="layered_kinematic",
        velocity_model_type="layered",
    )
    result = check_single_figure(
        path,
        expected_category="diagnostics",
        metadata=metadata[path.name],
        min_size_bytes=64,
        min_width_px=32,
        min_height_px=24,
    )
    assert result["passed"] is True


def test_figure_self_check_rejects_missing_and_old_stage(tmp_path):
    path = tmp_path / "figures" / "fig_velocity_model_active_badge.png"
    _write_nonblank_png(path)
    specs = [
        StableFigureSpec(
            "diagnostics",
            "fig_velocity_model_active_badge.png",
            "reports/diagnostics/report_velocity_model_audit.md",
        ),
        StableFigureSpec("forward", "fig_missing_stage5d.png", "reports/forward/report.md"),
    ]
    metadata = {
        "fig_velocity_model_active_badge.png": {
            "stage": "Stage 3",
            "forward_engine": "layered_kinematic",
            "velocity_model_type": "layered",
            "category": "diagnostics",
        },
        "fig_missing_stage5d.png": {
            "stage": "Stage 5D",
            "forward_engine": "layered_kinematic",
            "velocity_model_type": "layered",
            "category": "forward",
        },
    }
    result = run_figure_self_check(tmp_path, specs, metadata)
    assert result["failed_count"] == 2
    assert "fig_velocity_model_active_badge.png" in result["excluded_old_figures"]
