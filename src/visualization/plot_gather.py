"""炮集 QC 绘图。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_shot_gather(params: SimpleNamespace, data: np.ndarray, shot_index: int, output_path: Path) -> None:
    """绘制单炮 DAS-like 合成记录。

    输入参数：
        data：shape = (n_shot, n_time, n_channel)，即 shot × time × channel。

    输出：
        shot_gather_*.png。

    近似条件和限制：
        图件标题明确标注 kinematic approximation 和 DAS-like approximation，避免
        被误解为完整 DAS 仪器或完整三维弹性波模拟结果。
    """

    gather = data[shot_index, :, :]
    clip = np.percentile(np.abs(gather), 99.0)
    if clip == 0:
        clip = 1.0

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    extent = [
        float(params.derived.channel_x[0]),
        float(params.derived.channel_x[-1]),
        float(params.derived.time_axis[-1]),
        float(params.derived.time_axis[0]),
    ]
    image = ax.imshow(gather, aspect="auto", cmap="seismic", vmin=-clip, vmax=clip, extent=extent)
    ax.set_xlabel("channel x (m)")
    ax.set_ylabel("time (s)")
    ax.set_title(f"Shot {shot_index}: DAS-like response approximation, kinematic approximation")
    fig.colorbar(image, ax=ax, label="relative amplitude")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
