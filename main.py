"""hcz_void_plus 的统一入口与参数中心。

本文件是项目唯一参数中心。所有默认参数、命令行参数、派生参数和参数校验
都集中在这里；src、experiments、visualization 和 pipeline 中的算法模块只能
接收这里生成的 params 对象，不能再维护第二套局部参数。

坐标约定：
    x：沿道路和光纤方向，单位 m；
    y：横穿道路方向，单位 m，光纤近似位于 y=0，震源线近似位于 y=W；
    z / h：深度方向，向下为正，单位 m。
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable

import numpy as np


MAX_SCAN_GRID_POINTS = 250_000


def str_to_bool(value: str | bool) -> bool:
    """解析命令行布尔值。

    许多科研运行开关需要显式 true/false，例如是否保存伪波场快照、是否保存
    GIF、是否启用直达波 mute。统一解析可以避免不同脚本中出现不同布尔写法。
    """

    if isinstance(value, bool):
        return value
    lowered = value.lower()
    if lowered in {"true", "1", "yes", "y", "on"}:
        return True
    if lowered in {"false", "0", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"无法解析布尔值：{value}")


def build_arg_parser() -> argparse.ArgumentParser:
    """构建 argparse 参数解析器。

    参数按物理和流程含义分组。所有新增参数必须先进入这里，算法模块只能读取
    main.py 解析、派生和校验后的 params，保证正演、绘图、扫描和报告使用同一
    套场景定义。
    """

    parser = argparse.ArgumentParser(
        description="城市道路既有通信光纤 DAS-like 空洞探测：运动学正演与基础扫描定位"
    )

    project = parser.add_argument_group("project 参数组")
    project.add_argument(
        "--task",
        default="debug",
        choices=["debug", "forward", "full_pipeline", "scan", "robustness"],
        help="运行任务。scan/robustness 先作为接口预留；full_pipeline 会执行正演和基础扫描。",
    )
    project.add_argument("--run-name", default="stage2_run", help="本次运行名称，会和时间戳组成输出目录。")
    project.add_argument("--random-seed", type=int, default=20260703, help="随机种子，用于噪声和可复现实验。")

    road = parser.add_argument_group("road 道路参数组")
    road.add_argument("--road-width-m", type=float, default=18.0, help="道路横向宽度 W，单位 m。")
    road.add_argument("--road-length-m", type=float, default=120.0, help="道路沿 x 方向长度，单位 m。")
    road.add_argument("--road-surface-z-m", type=float, default=0.0, help="路面 z 坐标，单位 m；z 向下为正。")

    fiber = parser.add_argument_group("fiber 光纤参数组")
    fiber.add_argument("--fiber-y-m", type=float, default=0.0, help="光纤横向 y 坐标，典型单侧几何中近似为 0。")
    fiber.add_argument("--fiber-z-m", type=float, default=0.0, help="光纤等效接收深度，单位 m。")
    fiber.add_argument("--fiber-x-start-m", type=float, default=0.0, help="第一个 DAS-like 通道的 x 坐标，单位 m。")
    fiber.add_argument("--fiber-channel-spacing-m", type=float, default=1.0, help="相邻光纤通道间距，单位 m。")
    fiber.add_argument("--fiber-channel-count", type=int, default=121, help="光纤通道数量，是主参数。")

    source = parser.add_argument_group("source 震源参数组")
    source.add_argument("--source-y-m", type=float, default=None, help="震源线 y 坐标；未设置时自动等于 road_width_m。")
    source.add_argument("--source-z-m", type=float, default=0.0, help="震源 z 坐标，单位 m。")
    source.add_argument("--source-x-start-m", type=float, default=10.0, help="第一个炮点的 x 坐标，单位 m。")
    source.add_argument("--source-shot-spacing-m", type=float, default=10.0, help="相邻炮点间距，单位 m。")
    source.add_argument("--source-shot-count", type=int, default=9, help="炮点数量，是主参数。")
    source.add_argument(
        "--source-type",
        default="hammer",
        choices=["hammer", "drop_weight", "small_active", "vehicle"],
        help="震源类型标签，仅进入 metadata 和报告。",
    )

    time = parser.add_argument_group("time 时间采样参数组")
    time.add_argument("--time-dt-s", type=float, default=0.001, help="时间采样间隔，单位 s。")
    time.add_argument("--time-record-length-s", type=float, default=0.8, help="记录长度，单位 s。")
    time.add_argument("--time-t0-s", type=float, default=0.02, help="震源激发和记录参考零时之间的等效延迟，单位 s。")

    velocity = parser.add_argument_group("velocity 速度模型参数组")
    velocity.add_argument("--velocity-model-type", default="uniform", choices=["uniform"], help="Stage 2 仅实现 uniform。")
    velocity.add_argument("--rayleigh-velocity-mps", type=float, default=260.0, help="等效瑞雷波速度，单位 m/s。")

    anomaly = parser.add_argument_group("anomaly 异常体参数组")
    anomaly.add_argument("--anomaly-type", default="cavity", choices=["cavity"], help="异常体类型；Stage 2 支持 cavity。")
    anomaly.add_argument("--anomaly-x0-m", type=float, default=60.0, help="异常体中心 x 坐标，单位 m。")
    anomaly.add_argument("--anomaly-y0-m", type=float, default=9.0, help="异常体中心 y 坐标，单位 m。")
    anomaly.add_argument("--anomaly-depth-m", type=float, default=3.0, help="异常体中心深度 h，单位 m，向下为正。")
    anomaly.add_argument("--anomaly-radius-m", type=float, default=1.5, help="异常体等效半径，单位 m。")
    anomaly.add_argument("--scatter-strength", type=float, default=0.8, help="等效散射强度，无量纲。")
    anomaly.add_argument(
        "--scatter-point-mode",
        default="center_and_boundary",
        choices=["center", "center_and_boundary"],
        help="等效散射点表达方式。",
    )

    das_like = parser.add_argument_group("das_like DAS-like 接收参数组")
    das_like.add_argument(
        "--das-response-level",
        default="point_receiver",
        choices=["point_receiver"],
        help="DAS-like 响应层级；Stage 2 仍为点式接收近似。",
    )
    das_like.add_argument("--gauge-length-m", type=float, default=10.0, help="DAS gauge length 参数；point_receiver 不参与波形计算。")
    das_like.add_argument("--strain-rate", type=str_to_bool, default=False, help="应变率标签；Stage 2 仅进入 metadata。")

    noise = parser.add_argument_group("noise 噪声参数组")
    noise.add_argument("--noise-enabled", type=str_to_bool, default=False, help="是否加入高斯白噪声。")
    noise.add_argument("--noise-snr-db", type=float, default=20.0, help="目标信噪比，单位 dB。")

    output = parser.add_argument_group("output 输出参数组")
    output.add_argument("--output-root-dir", default="outputs", help="输出根目录。")
    output.add_argument("--save-figures", type=str_to_bool, default=True, help="是否保存静态图。")
    output.add_argument("--save-arrays", type=str_to_bool, default=True, help="是否保存 numpy 数组。")
    output.add_argument("--save-report", type=str_to_bool, default=True, help="是否保存 Markdown 报告。")
    output.add_argument("--figure-language", default="zh", choices=["zh", "en"], help="图件和报告的人类可读语言，默认中文。")
    output.add_argument("--max-shot-gather-figures", type=int, default=3, help="最多保存多少张炮集图。")
    output.add_argument("--save-wavefield-snapshots", type=str_to_bool, default=True, help="是否保存运动学伪波场快照。")
    output.add_argument("--save-wavefield-animation", type=str_to_bool, default=True, help="是否尝试保存运动学伪波场 GIF。")
    output.add_argument("--wavefield-snapshot-count", type=int, default=12, help="保存伪波场快照帧数。")
    output.add_argument("--wavefield-grid-nx", type=int, default=160, help="伪波场 x 方向网格数。")
    output.add_argument("--wavefield-grid-ny", type=int, default=80, help="伪波场 y 方向网格数。")
    output.add_argument("--wavefield-animation-fps", type=float, default=4.0, help="伪波场 GIF 帧率。")
    output.add_argument("--wavefield-shot-index", type=int, default=0, help="用于伪波场展示的炮点索引，从 0 开始。")
    output.add_argument("--output-prefix-style", default="compact", choices=["compact"], help="输出文件前缀规则，Stage 2 使用 compact。")
    output.add_argument(
        "--max-shot-figures",
        type=int,
        default=None,
        help="兼容 Stage 1 的旧参数；若设置，会覆盖 --max-shot-gather-figures。",
    )

    scan = parser.add_argument_group("scan 扫描定位参数组")
    scan.add_argument("--scan-enabled", type=str_to_bool, default=True, help="是否启用基础 x-y-h 多炮扫描定位。")
    scan.add_argument("--scan-x-min-m", type=float, default=20.0, help="扫描 x 最小值，单位 m。")
    scan.add_argument("--scan-x-max-m", type=float, default=180.0, help="扫描 x 最大值，单位 m。")
    scan.add_argument("--scan-x-step-m", type=float, default=2.0, help="扫描 x 步长，单位 m。")
    scan.add_argument("--scan-y-min-m", type=float, default=2.0, help="扫描 y 最小值，单位 m。")
    scan.add_argument("--scan-y-max-m", type=float, default=18.0, help="扫描 y 最大值，单位 m。")
    scan.add_argument("--scan-y-step-m", type=float, default=1.0, help="扫描 y 步长，单位 m。")
    scan.add_argument("--scan-depth-min-m", type=float, default=0.5, help="扫描深度最小值，单位 m。")
    scan.add_argument("--scan-depth-max-m", type=float, default=8.0, help="扫描深度最大值，单位 m。")
    scan.add_argument("--scan-depth-step-m", type=float, default=0.5, help="扫描深度步长，单位 m。")
    scan.add_argument(
        "--score-method",
        default="diffraction_energy_stack",
        choices=["diffraction_energy_stack"],
        help="扫描得分方法；Stage 2 采用绕射能量叠加。",
    )
    scan.add_argument("--direct-mute-enabled", type=str_to_bool, default=True, help="扫描前是否按预测直达波时间窗 mute。")
    scan.add_argument("--direct-mute-half-width-s", type=float, default=0.02, help="直达波 mute 半窗长，单位 s。")
    scan.add_argument("--scan-time-window-half-width-s", type=float, default=0.015, help="扫描能量拾取半窗长，单位 s。")
    scan.add_argument("--scan-use-depth-weight", type=str_to_bool, default=True, help="是否在扫描得分中加入 Rayleigh 波简化深度敏感性权重。")
    scan.add_argument("--rayleigh-penetration-factor", type=float, default=1.0, help="穿透深度系数：penetration_depth = factor * wavelength。")

    task = parser.add_argument_group("task 任务控制参数组")
    task.add_argument("--wavelet-frequency-hz", type=float, default=35.0, help="Ricker 子波主频，单位 Hz。")
    task.add_argument("--wavelet-dominant-frequency-hz", type=float, default=30.0, help="用于 Rayleigh 波深度敏感性估计的主频，单位 Hz。")

    return parser


def parse_arguments(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """解析命令行参数。测试可传入 argv，真实运行时使用系统参数。"""

    return build_arg_parser().parse_args(argv)


def _namespace(**kwargs: Any) -> SimpleNamespace:
    return SimpleNamespace(**kwargs)


def args_to_params(args: argparse.Namespace) -> SimpleNamespace:
    """将 argparse 的扁平参数转换为分组 params 对象。"""

    max_shot_gather_figures = (
        args.max_shot_figures if args.max_shot_figures is not None else args.max_shot_gather_figures
    )
    params = _namespace(
        project=_namespace(task=args.task, run_name=args.run_name, random_seed=args.random_seed),
        road=_namespace(width_m=args.road_width_m, length_m=args.road_length_m, surface_z_m=args.road_surface_z_m),
        fiber=_namespace(
            y_m=args.fiber_y_m,
            z_m=args.fiber_z_m,
            x_start_m=args.fiber_x_start_m,
            channel_spacing_m=args.fiber_channel_spacing_m,
            channel_count=args.fiber_channel_count,
        ),
        source=_namespace(
            y_m=args.source_y_m,
            z_m=args.source_z_m,
            x_start_m=args.source_x_start_m,
            shot_spacing_m=args.source_shot_spacing_m,
            shot_count=args.source_shot_count,
            source_type=args.source_type,
        ),
        time=_namespace(dt_s=args.time_dt_s, record_length_s=args.time_record_length_s, t0_s=args.time_t0_s),
        velocity=_namespace(model_type=args.velocity_model_type, rayleigh_velocity_mps=args.rayleigh_velocity_mps),
        anomaly=_namespace(
            anomaly_type=args.anomaly_type,
            x0_m=args.anomaly_x0_m,
            y0_m=args.anomaly_y0_m,
            depth_m=args.anomaly_depth_m,
            radius_m=args.anomaly_radius_m,
            scatter_strength=args.scatter_strength,
            scatter_point_mode=args.scatter_point_mode,
        ),
        das_like=_namespace(
            response_level=args.das_response_level,
            gauge_length_m=args.gauge_length_m,
            strain_rate=args.strain_rate,
        ),
        noise=_namespace(enabled=args.noise_enabled, snr_db=args.noise_snr_db),
        output=_namespace(
            root_dir=args.output_root_dir,
            save_figures=args.save_figures,
            save_arrays=args.save_arrays,
            save_report=args.save_report,
            figure_language=args.figure_language,
            max_shot_gather_figures=max_shot_gather_figures,
            save_wavefield_snapshots=args.save_wavefield_snapshots,
            save_wavefield_animation=args.save_wavefield_animation,
            wavefield_snapshot_count=args.wavefield_snapshot_count,
            wavefield_grid_nx=args.wavefield_grid_nx,
            wavefield_grid_ny=args.wavefield_grid_ny,
            wavefield_animation_fps=args.wavefield_animation_fps,
            wavefield_shot_index=args.wavefield_shot_index,
            prefix_style=args.output_prefix_style,
        ),
        scan=_namespace(
            enabled=args.scan_enabled,
            x_min_m=args.scan_x_min_m,
            x_max_m=args.scan_x_max_m,
            x_step_m=args.scan_x_step_m,
            y_min_m=args.scan_y_min_m,
            y_max_m=args.scan_y_max_m,
            y_step_m=args.scan_y_step_m,
            depth_min_m=args.scan_depth_min_m,
            depth_max_m=args.scan_depth_max_m,
            depth_step_m=args.scan_depth_step_m,
            score_method=args.score_method,
            direct_mute_enabled=args.direct_mute_enabled,
            direct_mute_half_width_s=args.direct_mute_half_width_s,
            time_window_half_width_s=args.scan_time_window_half_width_s,
            use_depth_weight=args.scan_use_depth_weight,
            rayleigh_penetration_factor=args.rayleigh_penetration_factor,
        ),
        task=_namespace(
            wavelet_frequency_hz=args.wavelet_frequency_hz,
            wavelet_dominant_frequency_hz=args.wavelet_dominant_frequency_hz,
        ),
        derived=_namespace(),
    )

    validate_raw_params(params)
    resolve_derived_params(params)
    validate_resolved_params(params)
    return params


def validate_raw_params(params: SimpleNamespace) -> None:
    """校验无需派生即可判断的原始参数。"""

    if params.road.width_m <= 0:
        raise ValueError(f"road_width_m 错误：当前值为 {params.road.width_m}，合理条件是道路宽度 > 0。")
    if params.road.length_m <= 0:
        raise ValueError(f"road_length_m 错误：当前值为 {params.road.length_m}，合理条件是道路长度 > 0。")
    if params.fiber.channel_spacing_m <= 0:
        raise ValueError(f"fiber_channel_spacing_m 错误：当前值为 {params.fiber.channel_spacing_m}，合理条件是通道间距 > 0。")
    if params.fiber.channel_count < 2:
        raise ValueError(f"fiber_channel_count 错误：当前值为 {params.fiber.channel_count}，合理条件是通道数量 >= 2。")
    if params.source.shot_spacing_m <= 0:
        raise ValueError(f"source_shot_spacing_m 错误：当前值为 {params.source.shot_spacing_m}，合理条件是炮点间距 > 0。")
    if params.source.shot_count < 1:
        raise ValueError(f"source_shot_count 错误：当前值为 {params.source.shot_count}，合理条件是炮点数量 >= 1。")
    if params.time.dt_s <= 0:
        raise ValueError(f"time_dt_s 错误：当前值为 {params.time.dt_s}，合理条件是采样间隔 > 0。")
    if params.time.record_length_s <= params.time.dt_s:
        raise ValueError(
            f"time_record_length_s 错误：当前值为 {params.time.record_length_s}，"
            f"采样间隔为 {params.time.dt_s}，合理条件是记录长度 > 采样间隔。"
        )
    if params.velocity.rayleigh_velocity_mps <= 0:
        raise ValueError(f"rayleigh_velocity_mps 错误：当前值为 {params.velocity.rayleigh_velocity_mps}，合理条件是速度 > 0。")
    if params.anomaly.depth_m <= 0:
        raise ValueError(f"anomaly_depth_m 错误：当前值为 {params.anomaly.depth_m}，合理条件是异常体深度 > 0。")
    if not (0.0 <= params.anomaly.y0_m <= params.road.width_m):
        raise ValueError(
            f"anomaly_y0_m 错误：当前值为 {params.anomaly.y0_m}，合理条件是 0 <= y <= {params.road.width_m}。"
        )
    if params.das_like.gauge_length_m < params.fiber.channel_spacing_m:
        raise ValueError(
            f"gauge_length_m 错误：当前值为 {params.das_like.gauge_length_m}，"
            f"通道间距为 {params.fiber.channel_spacing_m}，合理条件是 gauge length >= 通道间距。"
        )
    if not (-20.0 <= params.noise.snr_db <= 100.0):
        raise ValueError(f"noise_snr_db 错误：当前值为 {params.noise.snr_db}，合理条件是 -20 到 100 dB。")
    if params.output.max_shot_gather_figures < 0:
        raise ValueError(
            f"max_shot_gather_figures 错误：当前值为 {params.output.max_shot_gather_figures}，合理条件是 >= 0。"
        )
    if params.output.wavefield_snapshot_count < 1:
        raise ValueError(
            f"wavefield_snapshot_count 错误：当前值为 {params.output.wavefield_snapshot_count}，合理条件是 >= 1。"
        )
    if params.output.wavefield_grid_nx < 10:
        raise ValueError(f"wavefield_grid_nx 错误：当前值为 {params.output.wavefield_grid_nx}，合理条件是 >= 10。")
    if params.output.wavefield_grid_ny < 10:
        raise ValueError(f"wavefield_grid_ny 错误：当前值为 {params.output.wavefield_grid_ny}，合理条件是 >= 10。")
    if params.output.wavefield_animation_fps <= 0:
        raise ValueError(
            f"wavefield_animation_fps 错误：当前值为 {params.output.wavefield_animation_fps}，合理条件是 > 0。"
        )
    if params.scan.x_step_m <= 0:
        raise ValueError(f"scan_x_step_m 错误：当前值为 {params.scan.x_step_m}，合理条件是 > 0。")
    if params.scan.y_step_m <= 0:
        raise ValueError(f"scan_y_step_m 错误：当前值为 {params.scan.y_step_m}，合理条件是 > 0。")
    if params.scan.depth_step_m <= 0:
        raise ValueError(f"scan_depth_step_m 错误：当前值为 {params.scan.depth_step_m}，合理条件是 > 0。")
    if params.scan.x_min_m >= params.scan.x_max_m:
        raise ValueError(
            f"scan_x_min_m/scan_x_max_m 错误：当前值为 {params.scan.x_min_m}/{params.scan.x_max_m}，合理条件是 min < max。"
        )
    if params.scan.y_min_m >= params.scan.y_max_m:
        raise ValueError(
            f"scan_y_min_m/scan_y_max_m 错误：当前值为 {params.scan.y_min_m}/{params.scan.y_max_m}，合理条件是 min < max。"
        )
    if params.scan.depth_min_m >= params.scan.depth_max_m:
        raise ValueError(
            "scan_depth_min_m/scan_depth_max_m 错误："
            f"当前值为 {params.scan.depth_min_m}/{params.scan.depth_max_m}，合理条件是 min < max。"
        )
    if params.scan.direct_mute_half_width_s < 0:
        raise ValueError(
            f"direct_mute_half_width_s 错误：当前值为 {params.scan.direct_mute_half_width_s}，合理条件是 >= 0。"
        )
    if params.scan.time_window_half_width_s <= 0:
        raise ValueError(
            f"scan_time_window_half_width_s 错误：当前值为 {params.scan.time_window_half_width_s}，合理条件是 > 0。"
        )
    if params.scan.rayleigh_penetration_factor <= 0:
        raise ValueError(
            f"rayleigh_penetration_factor 错误：当前值为 {params.scan.rayleigh_penetration_factor}，合理条件是 > 0。"
        )
    if params.task.wavelet_frequency_hz <= 0:
        raise ValueError(f"wavelet_frequency_hz 错误：当前值为 {params.task.wavelet_frequency_hz}，合理条件是 > 0。")
    if params.task.wavelet_dominant_frequency_hz <= 0:
        raise ValueError(
            f"wavelet_dominant_frequency_hz 错误：当前值为 {params.task.wavelet_dominant_frequency_hz}，合理条件是 > 0。"
        )


def _make_inclusive_grid(start: float, stop: float, step: float) -> np.ndarray:
    """生成包含 stop 附近端点的一维扫描网格。"""

    count = int(np.floor((stop - start) / step)) + 1
    grid = start + np.arange(count, dtype=float) * step
    return grid[grid <= stop + 1.0e-9]


def resolve_derived_params(params: SimpleNamespace) -> None:
    """集中派生几何数组、时间轴、扫描网格和输出目录。"""

    if params.source.y_m is None:
        # 单侧 DAS-like 几何：光纤近似在 y=0，震源线默认在道路另一侧 y=W。
        params.source.y_m = params.road.width_m

    channel_indices = np.arange(params.fiber.channel_count, dtype=float)
    shot_indices = np.arange(params.source.shot_count, dtype=float)
    params.derived.channel_x = params.fiber.x_start_m + channel_indices * params.fiber.channel_spacing_m
    params.derived.shot_x = params.source.x_start_m + shot_indices * params.source.shot_spacing_m
    params.derived.fiber_x_end_m = float(params.derived.channel_x[-1])
    params.derived.source_x_end_m = float(params.derived.shot_x[-1])

    nt = int(np.floor(params.time.record_length_s / params.time.dt_s)) + 1
    params.derived.nt = nt
    params.derived.time_axis = np.arange(nt, dtype=float) * params.time.dt_s

    gauge_intervals = int(np.ceil(params.das_like.gauge_length_m / params.fiber.channel_spacing_m))
    params.derived.gauge_channel_count = gauge_intervals + 1

    params.derived.receiver_xyz = np.column_stack(
        [
            params.derived.channel_x,
            np.full(params.fiber.channel_count, params.fiber.y_m),
            np.full(params.fiber.channel_count, params.fiber.z_m),
        ]
    )
    params.derived.source_xyz = np.column_stack(
        [
            params.derived.shot_x,
            np.full(params.source.shot_count, params.source.y_m),
            np.full(params.source.shot_count, params.source.z_m),
        ]
    )

    params.derived.scan_x_grid = _make_inclusive_grid(params.scan.x_min_m, params.scan.x_max_m, params.scan.x_step_m)
    params.derived.scan_y_grid = _make_inclusive_grid(params.scan.y_min_m, params.scan.y_max_m, params.scan.y_step_m)
    params.derived.scan_depth_grid = _make_inclusive_grid(
        params.scan.depth_min_m, params.scan.depth_max_m, params.scan.depth_step_m
    )
    params.derived.scan_shape = (
        len(params.derived.scan_x_grid),
        len(params.derived.scan_y_grid),
        len(params.derived.scan_depth_grid),
    )
    params.derived.scan_grid_point_count = int(np.prod(params.derived.scan_shape))
    params.derived.estimated_wavelength_m = (
        params.velocity.rayleigh_velocity_mps / params.task.wavelet_dominant_frequency_hz
    )
    params.derived.rayleigh_penetration_depth_m = (
        params.scan.rayleigh_penetration_factor * params.derived.estimated_wavelength_m
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_run_name = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in params.project.run_name)
    params.derived.output_run_dir = str(Path(params.output.root_dir) / f"{safe_run_name}_{timestamp}")


def validate_resolved_params(params: SimpleNamespace) -> None:
    """校验派生后的完整参数对象。"""

    effective_fiber_length = params.derived.fiber_x_end_m - params.fiber.x_start_m
    if params.das_like.gauge_length_m > effective_fiber_length:
        raise ValueError(
            f"gauge_length_m 错误：当前值为 {params.das_like.gauge_length_m}，"
            f"光纤有效长度为 {effective_fiber_length}，合理条件是不大于光纤有效长度。"
        )
    if len(params.derived.channel_x) != params.fiber.channel_count:
        raise ValueError("channel_x 派生错误：数量必须等于 fiber_channel_count。")
    if len(params.derived.shot_x) != params.source.shot_count:
        raise ValueError("shot_x 派生错误：数量必须等于 source_shot_count。")
    if len(params.derived.time_axis) != params.derived.nt:
        raise ValueError("time_axis 派生错误：长度必须等于 nt。")
    if params.derived.receiver_xyz.shape != (params.fiber.channel_count, 3):
        raise ValueError(f"receiver_xyz 维度错误：当前 shape={params.derived.receiver_xyz.shape}。")
    if params.derived.source_xyz.shape != (params.source.shot_count, 3):
        raise ValueError(f"source_xyz 维度错误：当前 shape={params.derived.source_xyz.shape}。")
    if not (0 <= params.output.wavefield_shot_index < params.source.shot_count):
        raise ValueError(
            f"wavefield_shot_index 错误：当前值为 {params.output.wavefield_shot_index}，"
            f"合理条件是 0 <= index < {params.source.shot_count}。"
        )
    if params.derived.scan_grid_point_count > MAX_SCAN_GRID_POINTS:
        raise ValueError(
            f"扫描网格点数过大：当前为 {params.derived.scan_grid_point_count}，"
            f"上限为 {MAX_SCAN_GRID_POINTS}。请增大步长或缩小扫描范围。"
        )
    try:
        Path(params.output.root_dir).mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ValueError(f"output_root_dir 错误：无法创建输出根目录 {params.output.root_dir}，原因：{exc}") from exc


def print_params_summary(params: SimpleNamespace) -> None:
    """在终端打印本次运行摘要。"""

    print("=== hcz_void_plus Stage 2 参数摘要 ===")
    print(f"task: {params.project.task}")
    print(f"run_name: {params.project.run_name}")
    print(f"road width/length: {params.road.width_m} m / {params.road.length_m} m")
    print(f"fiber channels: {params.fiber.channel_count}, x=[{params.fiber.x_start_m}, {params.derived.fiber_x_end_m}] m")
    print(f"shots: {params.source.shot_count}, source_y={params.source.y_m} m")
    print(f"time: nt={params.derived.nt}, dt={params.time.dt_s} s")
    print(f"scan grid: {params.derived.scan_shape}, points={params.derived.scan_grid_point_count}")
    print(
        "rayleigh depth sensitivity: "
        f"wavelength={params.derived.estimated_wavelength_m:.3f} m, "
        f"penetration_depth={params.derived.rayleigh_penetration_depth_m:.3f} m"
    )
    print("approximation: kinematic approximation + DAS-like response approximation")
    print(f"output_run_dir: {params.derived.output_run_dir}")


def create_output_dir(params: SimpleNamespace) -> Path:
    """创建本次运行独立输出根目录。"""

    output_run_dir = Path(params.derived.output_run_dir)
    output_run_dir.mkdir(parents=True, exist_ok=True)
    return output_run_dir


def dispatch_task(params: SimpleNamespace) -> dict[str, Any]:
    """根据 --task 调度科研流程。"""

    create_output_dir(params)
    print_params_summary(params)

    if params.project.task in {"debug", "forward"}:
        from src.pipeline.run_forward_pipeline import run_forward_pipeline

        return run_forward_pipeline(params)
    if params.project.task == "full_pipeline":
        from src.pipeline.run_full_pipeline import run_full_pipeline

        return run_full_pipeline(params)
    if params.project.task == "scan":
        from src.pipeline.run_full_pipeline import run_full_pipeline

        return run_full_pipeline(params)
    raise ValueError(f"task={params.project.task} 已预留，但 Stage 2 尚未实现该独立流程。")


def main(argv: Iterable[str] | None = None) -> dict[str, Any]:
    """命令行总入口。"""

    args = parse_arguments(argv)
    params = args_to_params(args)
    return dispatch_task(params)


if __name__ == "__main__":
    main()
