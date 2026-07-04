from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from src.validation.figure_quality_check import check_figure_quality, run_figure_quality_check


def _save_image(path: Path, data: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.imsave(path, data, cmap="viridis")


def test_figure_quality_check_rejects_blank_and_accepts_data(tmp_path):
    blank = tmp_path / "blank.png"
    data = tmp_path / "data.png"
    _save_image(blank, np.ones((300, 300)))
    _save_image(data, np.random.default_rng(1).normal(size=(300, 300)))

    assert check_figure_quality(blank)["passed"] is False
    assert check_figure_quality(data)["passed"] is True


def test_run_figure_quality_check_scans_latest_like_tree(tmp_path):
    latest = tmp_path / "latest_stable"
    _save_image(latest / "figures" / "core" / "fig_ok.png", np.random.default_rng(2).normal(size=(300, 300)))
    result = run_figure_quality_check(latest)
    assert result["checked_count"] == 1
    assert result["empty_figure_count"] == 0
    assert result["status"] == "pass"
