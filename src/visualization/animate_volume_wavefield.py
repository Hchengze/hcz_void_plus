"""三维运动学体响应 proxy 动图。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

from src.visualization.plot_style import setup_chinese_matplotlib


def _nearest_index(axis: np.ndarray, value: float) -> int:
    return int(np.argmin(np.abs(np.asarray(axis, dtype=float) - float(value))))


def save_single_shot_volume_wavefield_animation(
    params: SimpleNamespace,
    volume_response: dict[str, Any],
    output_path: Path,
) -> dict[str, object]:
    """保存单炮 x-y-depth 体响应 proxy GIF。

    GIF 展示三个正交切片，不声称是真实弹性波场。
    """

    if not params.output.save_wavefield_animation:
        return {"success": False, "path": None, "reason": "save_wavefield_animation=False"}

    setup_chinese_matplotlib()
    frames = np.asarray(volume_response["volume_frames"], dtype=float)
    times = np.asarray(volume_response["time_axis_s"], dtype=float)
    x = np.asarray(volume_response["x_axis_m"], dtype=float)
    y = np.asarray(volume_response["y_axis_m"], dtype=float)
    h = np.asarray(volume_response["depth_axis_m"], dtype=float)
    ix = _nearest_index(x, params.anomaly.x0_m)
    iy = _nearest_index(y, params.anomaly.y0_m)
    ih = _nearest_index(h, params.anomaly.depth_m)
    clip = float(np.percentile(np.abs(frames), 99.0)) or 1.0

    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.8), dpi=120)

    def draw(frame_index: int):
        for ax in axes:
            ax.clear()
        frame = frames[frame_index]
        axes[0].imshow(
            frame[ih],
            extent=[x.min(), x.max(), y.min(), y.max()],
            origin="lower",
            cmap="seismic",
            vmin=-clip,
            vmax=clip,
            aspect="auto",
        )
        axes[0].scatter([params.anomaly.x0_m], [params.anomaly.y0_m], marker="x", color="black", s=50)
        axes[0].set_title(f"x-y，h={h[ih]:.1f} m")
        axes[0].set_xlabel("x / m")
        axes[0].set_ylabel("y / m")

        axes[1].imshow(
            frame[:, iy, :],
            extent=[x.min(), x.max(), h.max(), h.min()],
            cmap="seismic",
            vmin=-clip,
            vmax=clip,
            aspect="auto",
        )
        axes[1].scatter([params.anomaly.x0_m], [params.anomaly.depth_m], marker="x", color="black", s=50)
        axes[1].set_title(f"x-depth，y={y[iy]:.1f} m")
        axes[1].set_xlabel("x / m")
        axes[1].set_ylabel("深度 h / m")

        axes[2].imshow(
            frame[:, :, ix],
            extent=[y.min(), y.max(), h.max(), h.min()],
            cmap="seismic",
            vmin=-clip,
            vmax=clip,
            aspect="auto",
        )
        axes[2].scatter([params.anomaly.y0_m], [params.anomaly.depth_m], marker="x", color="black", s=50)
        axes[2].set_title(f"y-depth，x={x[ix]:.1f} m")
        axes[2].set_xlabel("y / m")
        axes[2].set_ylabel("深度 h / m")

        fig.suptitle(f"三维运动学体响应 proxy t={times[frame_index]:.3f}s（非 elastic wavefield）")
        fig.tight_layout()
        return list(axes)

    try:
        animation = FuncAnimation(fig, draw, frames=len(times), blit=False)
        writer = PillowWriter(fps=params.output.wavefield_animation_fps)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        animation.save(output_path, writer=writer)
        plt.close(fig)
        return {"success": True, "path": str(output_path), "reason": None}
    except Exception as exc:  # noqa: BLE001 - GIF 失败不应中断主算法验证
        plt.close(fig)
        return {"success": False, "path": None, "reason": str(exc)}
