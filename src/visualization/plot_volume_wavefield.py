"""三维运动学体响应 proxy 绘图。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any
import warnings

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.visualization.plot_style import setup_chinese_matplotlib


def _save(fig: plt.Figure, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # 3D axes 与共享 colorbar 组合时 matplotlib 会提示 tight_layout 兼容性；
    # 这里图件尺寸已经固定，局部屏蔽该布局提示，避免测试和日志被非算法问题淹没。
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="This figure includes Axes that are not compatible with tight_layout")
        fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _nearest_index(axis: np.ndarray, value: float) -> int:
    return int(np.argmin(np.abs(np.asarray(axis, dtype=float) - float(value))))


def plot_volume_wavefield_xyz_slices(
    params: SimpleNamespace,
    volume_response: dict[str, Any],
    output_path: Path,
) -> None:
    """绘制同一时刻的 x-y、x-depth、y-depth 三切片。"""

    setup_chinese_matplotlib()
    frames = np.asarray(volume_response["volume_frames"], dtype=float)
    times = np.asarray(volume_response["time_axis_s"], dtype=float)
    x = np.asarray(volume_response["x_axis_m"], dtype=float)
    y = np.asarray(volume_response["y_axis_m"], dtype=float)
    h = np.asarray(volume_response["depth_axis_m"], dtype=float)
    iframe = int(np.argmax(np.max(np.abs(frames), axis=(1, 2, 3))))
    frame = frames[iframe]
    ix = _nearest_index(x, params.anomaly.x0_m)
    iy = _nearest_index(y, params.anomaly.y0_m)
    ih = _nearest_index(h, params.anomaly.depth_m)
    clip = float(np.percentile(np.abs(frame), 99.0)) or 1.0

    fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.2), dpi=150)
    im0 = axes[0].imshow(
        frame[ih],
        extent=[x.min(), x.max(), y.min(), y.max()],
        origin="lower",
        cmap="seismic",
        vmin=-clip,
        vmax=clip,
        aspect="auto",
    )
    axes[0].scatter([params.anomaly.x0_m], [params.anomaly.y0_m], marker="x", color="black", s=70, label="异常体")
    axes[0].set_title(f"x-y 切片，深度={h[ih]:.1f} m")
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
    axes[1].scatter([params.anomaly.x0_m], [params.anomaly.depth_m], marker="x", color="black", s=70, label="异常体")
    axes[1].set_title(f"x-depth 切片，y={y[iy]:.1f} m")
    axes[1].set_xlabel("x / m")
    axes[1].set_ylabel("深度 h / m（向下为正）")

    axes[2].imshow(
        frame[:, :, ix],
        extent=[y.min(), y.max(), h.max(), h.min()],
        cmap="seismic",
        vmin=-clip,
        vmax=clip,
        aspect="auto",
    )
    axes[2].scatter([params.anomaly.y0_m], [params.anomaly.depth_m], marker="x", color="black", s=70, label="异常体")
    axes[2].set_title(f"y-depth 切片，x={x[ix]:.1f} m")
    axes[2].set_xlabel("y / m")
    axes[2].set_ylabel("深度 h / m（向下为正）")

    for ax in axes:
        ax.legend(loc="upper right", fontsize=7)
    fig.suptitle(f"三维运动学体响应 proxy，t={times[iframe]:.3f}s（不是真实 elastic wavefield）")
    fig.colorbar(im0, ax=axes.ravel().tolist(), shrink=0.82, label="相对振幅")
    _save(fig, output_path)


def plot_volume_wavefield_depth_slices(
    params: SimpleNamespace,
    volume_response: dict[str, Any],
    output_path: Path,
) -> None:
    """绘制多个深度上的 x-y 能量切片。"""

    setup_chinese_matplotlib()
    energy = np.asarray(volume_response["energy_volume"], dtype=float)
    x = np.asarray(volume_response["x_axis_m"], dtype=float)
    y = np.asarray(volume_response["y_axis_m"], dtype=float)
    h = np.asarray(volume_response["depth_axis_m"], dtype=float)
    depth_targets = np.linspace(h.min(), h.max(), 4)
    indices = [_nearest_index(h, value) for value in depth_targets]
    clip = float(np.percentile(np.abs(energy), 99.0)) or 1.0

    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.2), dpi=150)
    for ax, ih in zip(axes.ravel(), indices):
        im = ax.imshow(
            energy[ih],
            extent=[x.min(), x.max(), y.min(), y.max()],
            origin="lower",
            cmap="magma",
            vmin=0.0,
            vmax=clip,
            aspect="auto",
        )
        ax.scatter([params.anomaly.x0_m], [params.anomaly.y0_m], marker="x", color="cyan", s=65)
        ax.set_title(f"x-y 能量 proxy，深度={h[ih]:.1f} m")
        ax.set_xlabel("x / m")
        ax.set_ylabel("y / m")
    fig.suptitle("三维运动学体响应 proxy 深度切片（深度向下为正）")
    fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.82, label="max |amplitude|")
    _save(fig, output_path)


def plot_volume_wavefield_3d_energy_proxy(
    params: SimpleNamespace,
    volume_response: dict[str, Any],
    output_path: Path,
) -> None:
    """绘制三维高能量 proxy 点云。"""

    setup_chinese_matplotlib()
    energy = np.asarray(volume_response["energy_volume"], dtype=float)
    x = np.asarray(volume_response["x_axis_m"], dtype=float)
    y = np.asarray(volume_response["y_axis_m"], dtype=float)
    h = np.asarray(volume_response["depth_axis_m"], dtype=float)
    threshold = np.percentile(energy, 97.5)
    ih, iy, ix = np.where(energy >= threshold)
    values = energy[ih, iy, ix]

    fig = plt.figure(figsize=(8.8, 6.2), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    sc = ax.scatter(x[ix], y[iy], h[ih], c=values, cmap="magma", s=18, alpha=0.72)
    ax.scatter(
        [params.anomaly.x0_m],
        [params.anomaly.y0_m],
        [params.anomaly.depth_m],
        marker="x",
        s=90,
        color="cyan",
        linewidths=2.0,
        label="异常体真值",
    )
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.set_zlabel("深度 h / m（向下为正）")
    ax.invert_zaxis()
    ax.set_title("三维运动学体响应高能量 proxy（不是真实 elastic wavefield）")
    ax.legend(loc="upper left")
    fig.colorbar(sc, ax=ax, shrink=0.70, label="max |amplitude|")
    _save(fig, output_path)
