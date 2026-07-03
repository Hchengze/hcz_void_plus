"""预处理前后对比图。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.visualization.plot_style import setup_chinese_matplotlib


def plot_preprocessing_comparison(
    params: SimpleNamespace,
    raw_data: np.ndarray,
    processed_data: np.ndarray,
    output_path: Path,
    shot_index: int = 0,
) -> None:
    """绘制同一炮预处理前后炮集对比。"""

    setup_chinese_matplotlib()
    extent = [
        params.derived.channel_x[0],
        params.derived.channel_x[-1],
        params.derived.time_axis[-1],
        params.derived.time_axis[0],
    ]
    vmax = max(float(np.max(np.abs(raw_data[shot_index]))), float(np.max(np.abs(processed_data[shot_index]))), 1.0e-12)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), dpi=150, sharey=True)
    for ax, data, title in [
        (axes[0], raw_data[shot_index], "预处理前"),
        (axes[1], processed_data[shot_index], "预处理后"),
    ]:
        image = ax.imshow(data, aspect="auto", extent=extent, cmap="seismic", vmin=-vmax, vmax=vmax)
        ax.set_xlabel("通道 x / m")
        ax.set_title(title)
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    axes[0].set_ylabel("时间 / s")
    fig.suptitle("扫描输入预处理对比", fontsize=12)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)

