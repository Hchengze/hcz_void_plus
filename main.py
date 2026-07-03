"""hcz_void_plus 的统一入口与参数中心。

本文件是本项目 Stage 1 的总入口。所有默认参数、命令行覆盖参数、派生参数
和参数校验都集中在这里，算法模块只接收这里生成的 params 对象。

坐标约定：
    x：沿道路和光纤方向，单位 m；
    y：横穿道路方向，单位 m，光纤近似位于 y=0，震源线近似位于 y=W；
    z：深度方向，向下为正，单位 m。
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable

import numpy as np


def str_to_bool(value: str | bool) -> bool:
    """解析命令行布尔值。

    物理和输出参数中有一些开关，例如是否加入噪声、是否保存图件。使用显式
    true/false 可以避免 argparse 的 store_true 在默认值和覆盖值之间产生歧义。
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

    参数按科研含义分组，而不是按代码模块分组。这样做的目的，是让道路几何、
    光纤几何、震源几何、时间采样、速度模型、异常体和输出行为在同一个入口
    中被统一管理，避免算法模块各自维护一套局部参数。
    """

    parser = argparse.ArgumentParser(
        description=(
            "城市道路既有通信光纤 DAS-like 空洞探测："
            "Stage 1 运动学等效散射正演骨架"
        )
    )

    project = parser.add_argument_group("project 参数组")
    project.add_argument("--task", default="debug", choices=["debug", "forward", "full_pipeline", "scan", "robustness"], help="运行任务。scan/robustness 为后续阶段预留。")
    project.add_argument("--run-name", default="stage1_forward", help="本次运行名称，会和时间戳一起组成输出目录名。")
    project.add_argument("--random-seed", type=int, default=20260703, help="随机种子，用于噪声和可复现实验。")

    road = parser.add_argument_group("road 道路参数组")
    road.add_argument("--road-width-m", type=float, default=18.0, help="道路横向宽度 W，单位 m。")
    road.add_argument("--road-length-m", type=float, default=120.0, help="道路沿 x 方向长度，单位 m。")
    road.add_argument("--road-surface-z-m", type=float, default=0.0, help="路面 z 坐标，单位 m；本项目约定 z 向下为正。")

    fiber = parser.add_argument_group("fiber 光纤参数组")
    fiber.add_argument("--fiber-y-m", type=float, default=0.0, help="光纤横向 y 坐标，典型单侧几何中近似为 0。")
    fiber.add_argument("--fiber-z-m", type=float, default=0.0, help="光纤埋深/等效接收深度，单位 m。")
    fiber.add_argument("--fiber-x-start-m", type=float, default=0.0, help="第一个 DAS-like 通道的 x 坐标，单位 m。")
    fiber.add_argument("--fiber-channel-spacing-m", type=float, default=1.0, help="相邻光纤通道间距，单位 m。")
    fiber.add_argument("--fiber-channel-count", type=int, default=121, help="光纤通道数量，是主参数；末端坐标由程序派生。")

    source = parser.add_argument_group("source 震源参数组")
    source.add_argument("--source-y-m", type=float, default=None, help="震源线 y 坐标；若不设置，则自动等于 road_width_m。")
    source.add_argument("--source-z-m", type=float, default=0.0, help="震源 z 坐标，单位 m。")
    source.add_argument("--source-x-start-m", type=float, default=10.0, help="第一个炮点的 x 坐标，单位 m。")
    source.add_argument("--source-shot-spacing-m", type=float, default=10.0, help="相邻炮点间距，单位 m。")
    source.add_argument("--source-shot-count", type=int, default=9, help="炮点数量，是主参数；末端坐标由程序派生。")
    source.add_argument("--source-type", default="hammer", choices=["hammer", "drop_weight", "small_active", "vehicle"], help="震源类型标签，仅进入 metadata。")

    time = parser.add_argument_group("time 时间采样参数组")
    time.add_argument("--time-dt-s", type=float, default=0.001, help="时间采样间隔，单位 s。")
    time.add_argument("--time-record-length-s", type=float, default=0.8, help="记录长度，单位 s。")
    time.add_argument("--time-t0-s", type=float, default=0.02, help="震源激发和记录参考零时之间的等效延迟，单位 s。")

    velocity = parser.add_argument_group("velocity 速度模型参数组")
    velocity.add_argument("--velocity-model-type", default="uniform", choices=["uniform"], help="速度模型类型；Stage 1 仅实现 uniform。")
    velocity.add_argument("--rayleigh-velocity-mps", type=float, default=260.0, help="等效瑞雷波速度，单位 m/s。")

    anomaly = parser.add_argument_group("anomaly 异常体参数组")
    anomaly.add_argument("--anomaly-type", default="cavity", choices=["cavity"], help="异常体类型；Stage 1 至少支持 cavity。")
    anomaly.add_argument("--anomaly-x0-m", type=float, default=60.0, help="异常体中心 x 坐标，单位 m。")
    anomaly.add_argument("--anomaly-y0-m", type=float, default=9.0, help="异常体中心 y 坐标，单位 m。")
    anomaly.add_argument("--anomaly-depth-m", type=float, default=3.0, help="异常体中心深度 h，单位 m，z 向下为正。")
    anomaly.add_argument("--anomaly-radius-m", type=float, default=1.5, help="异常体等效半径，单位 m。")
    anomaly.add_argument("--scatter-strength", type=float, default=0.8, help="等效散射强度，无量纲。")
    anomaly.add_argument("--scatter-point-mode", default="center_and_boundary", choices=["center", "center_and_boundary"], help="等效散射点表达方式。")

    das_like = parser.add_argument_group("das_like DAS-like 接收参数组")
    das_like.add_argument("--das-response-level", default="point_receiver", choices=["point_receiver"], help="DAS-like 响应层级；Stage 1 仅实现点式接收近似。")
    das_like.add_argument("--gauge-length-m", type=float, default=10.0, help="DAS gauge length 参数，单位 m；point_receiver 阶段不参与波形计算。")
    das_like.add_argument("--strain-rate", type=str_to_bool, default=False, help="是否输出应变率类标签；Stage 1 仅进入 metadata。")

    noise = parser.add_argument_group("noise 噪声参数组")
    noise.add_argument("--noise-enabled", type=str_to_bool, default=False, help="是否加入高斯白噪声。")
    noise.add_argument("--noise-snr-db", type=float, default=20.0, help="目标信噪比，单位 dB。")

    output = parser.add_argument_group("output 输出参数组")
    output.add_argument("--output-root-dir", default="outputs", help="输出根目录。")
    output.add_argument("--save-figures", type=str_to_bool, default=True, help="是否保存几何图和炮集图。")
    output.add_argument("--save-arrays", type=str_to_bool, default=True, help="是否保存 numpy 数组。")
    output.add_argument("--save-report", type=str_to_bool, default=True, help="是否保存 Markdown 报告。")

    task = parser.add_argument_group("task 任务控制参数组")
    task.add_argument("--max-shot-figures", type=int, default=3, help="最多保存多少张炮集 QC 图。")
    task.add_argument("--wavelet-frequency-hz", type=float, default=35.0, help="Ricker 子波主频，单位 Hz。")

    return parser


def parse_arguments(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """解析命令行参数。

    测试可传入 argv，真实命令行运行时使用系统参数。解析完成后尚未派生任何
    几何数组，因此 source_y_m 仍可能为 None。
    """

    return build_arg_parser().parse_args(argv)


def _namespace(**kwargs: Any) -> SimpleNamespace:
    return SimpleNamespace(**kwargs)


def args_to_params(args: argparse.Namespace) -> SimpleNamespace:
    """将 argparse 的扁平参数转换为分组 params 对象。

    params 是算法模块唯一可见的参数对象。这里先保留原始命令行含义，再经过
    raw 校验、派生参数解析和 resolved 校验，保证传入 src/ 的参数已经自洽。
    """

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
        ),
        task=_namespace(max_shot_figures=args.max_shot_figures, wavelet_frequency_hz=args.wavelet_frequency_hz),
        derived=_namespace(),
    )

    validate_raw_params(params)
    resolve_derived_params(params)
    validate_resolved_params(params)
    return params


def validate_raw_params(params: SimpleNamespace) -> None:
    """校验用户直接给出的原始参数。

    raw 校验只检查无需派生即可判断的条件。错误信息使用中文，并同时给出当前
    值和合理条件，便于科研调参时快速定位问题。
    """

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
        raise ValueError(
            f"rayleigh_velocity_mps 错误：当前值为 {params.velocity.rayleigh_velocity_mps}，合理条件是瑞雷波速度 > 0。"
        )
    if params.anomaly.depth_m <= 0:
        raise ValueError(f"anomaly_depth_m 错误：当前值为 {params.anomaly.depth_m}，合理条件是异常体深度 > 0。")
    if not (0.0 <= params.anomaly.y0_m <= params.road.width_m):
        raise ValueError(
            f"anomaly_y0_m 错误：当前值为 {params.anomaly.y0_m}，"
            f"合理条件是位于道路范围 0 <= y <= {params.road.width_m}。"
        )
    if params.das_like.gauge_length_m < params.fiber.channel_spacing_m:
        raise ValueError(
            f"gauge_length_m 错误：当前值为 {params.das_like.gauge_length_m}，"
            f"通道间距为 {params.fiber.channel_spacing_m}，合理条件是 gauge length >= 通道间距。"
        )
    if not (-20.0 <= params.noise.snr_db <= 100.0):
        raise ValueError(f"noise_snr_db 错误：当前值为 {params.noise.snr_db}，合理条件是 -20 到 100 dB 的研究范围。")
    if params.task.max_shot_figures < 0:
        raise ValueError(f"max_shot_figures 错误：当前值为 {params.task.max_shot_figures}，合理条件是 >= 0。")
    if params.task.wavelet_frequency_hz <= 0:
        raise ValueError(
            f"wavelet_frequency_hz 错误：当前值为 {params.task.wavelet_frequency_hz}，合理条件是 Ricker 主频 > 0。"
        )


def resolve_derived_params(params: SimpleNamespace) -> None:
    """由主参数派生几何数组、时间轴和输出目录。

    这里集中处理所有“由一个参数自动推出另一个参数”的逻辑。例如通道数量是
    主参数，光纤末端 x 坐标由通道数量和间距派生；炮点数量也是主参数，炮线
    末端坐标由炮数和炮间距派生。算法模块不能再次私自推导这些值。
    """

    if params.source.y_m is None:
        # 单侧 DAS-like 典型几何：光纤在 y=0，震源线在道路另一侧 y=W。
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

    # gauge_channel_count 表示一个 gauge length 覆盖的离散通道数。Stage 1 的
    # point_receiver 近似不使用它参与波形计算，但仍派生并写入 metadata。
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

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_run_name = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in params.project.run_name)
    params.derived.output_run_dir = str(Path(params.output.root_dir) / f"{safe_run_name}_{timestamp}")


def validate_resolved_params(params: SimpleNamespace) -> None:
    """校验派生后的完整参数对象。

    resolved 校验关注需要派生量才能判断的条件，例如 gauge length 是否超过光纤
    有效长度、时间轴长度是否等于 nt、输出目录根路径是否可创建。
    """

    effective_fiber_length = params.derived.fiber_x_end_m - params.fiber.x_start_m
    if params.das_like.gauge_length_m > effective_fiber_length:
        raise ValueError(
            f"gauge_length_m 错误：当前值为 {params.das_like.gauge_length_m}，"
            f"光纤有效长度为 {effective_fiber_length}，合理条件是不大于光纤有效长度。"
        )
    if len(params.derived.channel_x) != params.fiber.channel_count:
        raise ValueError(
            f"channel_x 派生错误：当前数量为 {len(params.derived.channel_x)}，"
            f"应等于 fiber_channel_count={params.fiber.channel_count}。"
        )
    if len(params.derived.shot_x) != params.source.shot_count:
        raise ValueError(
            f"shot_x 派生错误：当前数量为 {len(params.derived.shot_x)}，"
            f"应等于 source_shot_count={params.source.shot_count}。"
        )
    if len(params.derived.time_axis) != params.derived.nt:
        raise ValueError(
            f"time_axis 派生错误：当前长度为 {len(params.derived.time_axis)}，应等于 nt={params.derived.nt}。"
        )
    if params.derived.receiver_xyz.shape != (params.fiber.channel_count, 3):
        raise ValueError(
            f"receiver_xyz 维度错误：当前 shape={params.derived.receiver_xyz.shape}，"
            f"合理条件是 ({params.fiber.channel_count}, 3)。"
        )
    if params.derived.source_xyz.shape != (params.source.shot_count, 3):
        raise ValueError(
            f"source_xyz 维度错误：当前 shape={params.derived.source_xyz.shape}，"
            f"合理条件是 ({params.source.shot_count}, 3)。"
        )

    try:
        Path(params.output.root_dir).mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ValueError(f"output_root_dir 错误：无法创建输出根目录 {params.output.root_dir}，原因：{exc}") from exc


def print_params_summary(params: SimpleNamespace) -> None:
    """在终端打印最小参数摘要，便于确认本次运行场景。"""

    print("=== hcz_void_plus Stage 1 参数摘要 ===")
    print(f"task: {params.project.task}")
    print(f"run_name: {params.project.run_name}")
    print(f"road width/length: {params.road.width_m} m / {params.road.length_m} m")
    print(f"fiber channels: {params.fiber.channel_count}, x=[{params.fiber.x_start_m}, {params.derived.fiber_x_end_m}] m")
    print(f"shots: {params.source.shot_count}, source_y={params.source.y_m} m")
    print(f"time: nt={params.derived.nt}, dt={params.time.dt_s} s")
    print("approximation: kinematic approximation + DAS-like response approximation")
    print(f"output_run_dir: {params.derived.output_run_dir}")


def create_output_dir(params: SimpleNamespace) -> Path:
    """创建本次运行独立输出目录。

    只创建 outputs/<run_name>_<timestamp> 这一类结果目录，不创建 config 或 para
    目录。后续数组、图件、报告、日志目录由 pipeline 统一创建。
    """

    output_run_dir = Path(params.derived.output_run_dir)
    output_run_dir.mkdir(parents=True, exist_ok=True)
    return output_run_dir


def dispatch_task(params: SimpleNamespace) -> dict[str, Any]:
    """根据 --task 调度科研流程。

    debug 和 forward 都走同一套 run_forward_pipeline，不维护第二套算法逻辑；
    full_pipeline 当前调用 forward，并在报告中诚实标注 scan/confidence/robustness
    属于后续阶段。
    """

    create_output_dir(params)
    print_params_summary(params)

    if params.project.task in {"debug", "forward"}:
        from src.pipeline.run_forward_pipeline import run_forward_pipeline

        return run_forward_pipeline(params)
    if params.project.task == "full_pipeline":
        from src.pipeline.run_full_pipeline import run_full_pipeline

        return run_full_pipeline(params)
    raise ValueError(f"task={params.project.task} 已预留，但 Stage 1 尚未实现。")


def main(argv: Iterable[str] | None = None) -> dict[str, Any]:
    """命令行总入口。"""

    args = parse_arguments(argv)
    params = args_to_params(args)
    return dispatch_task(params)


if __name__ == "__main__":
    main()
