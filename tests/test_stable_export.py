from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.utils.stable_export import export_latest_stable_outputs


def _touch(path: Path, text: str = "x"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_valid_png(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    image = np.outer(np.linspace(0.0, 1.0, 64), np.linspace(1.0, 0.0, 96))
    fig, ax = plt.subplots(figsize=(3.2, 2.4), dpi=100)
    ax.imshow(image, cmap="viridis")
    ax.set_axis_off()
    fig.savefig(path)
    plt.close(fig)


def test_export_latest_stable_outputs_creates_curated_directory(tmp_path):
    run_dir = tmp_path / "stage3_run_20260703_000000"
    latest = tmp_path / "latest_stable"
    _write_valid_png(run_dir / "figures" / "fig_geometry_layout_check.png")
    _write_valid_png(run_dir / "figures" / "fig_confidence_diagnostics.png")
    _write_valid_png(run_dir / "figures" / "unselected_extra.png")
    _touch(run_dir / "reports" / "report_full_pipeline.md")
    _touch(run_dir / "reports" / "report_confidence.md")
    _touch(run_dir / "metadata" / "meta_run.json", "{}")
    _touch(run_dir / "metadata" / "params_snapshot.json", "{}")
    _touch(run_dir / "arrays" / "arr_score_volume.npy")

    info = export_latest_stable_outputs(
        run_dir,
        latest,
        {
            "commit_id": "abc1234",
            "task_name": "pytest",
            "source_run_dir": str(run_dir),
            "confidence": {
                "peak": {"peak_sharpness": 2.0},
                "contrast": {"score_contrast": 3.0, "score_percentile": 100.0},
                "multi_shot_consistency": {"coefficient_of_variation": 0.2},
                "y_depth_coupling": {"warning": False},
                "low_confidence_flag": "high",
            },
        },
    )

    assert latest.exists()
    assert (latest / "README.md").exists()
    assert (latest / "archive_manifest.md").exists()
    assert (latest / "figures" / "core" / "fig_geometry_layout_check.png").exists()
    assert (latest / "figures" / "core" / "fig_confidence_diagnostics.png").exists()
    assert not (latest / "figures" / "unselected_extra.png").exists()
    assert len(list((latest / "figures").glob("*.png"))) == 0
    assert not (latest / "arrays").exists()
    assert (latest / "reports" / "core" / "report_confidence.md").exists()
    assert (latest / "metadata" / "meta_run.json").exists()
    assert (latest / "metadata" / "meta_params_snapshot.json").exists()
    assert (latest / "summary.md").exists()
    assert "abc1234" in (latest / "summary.md").read_text(encoding="utf-8")
    assert info["copied"]
