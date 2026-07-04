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
    project.add_argument("--run-name", default="stage5f_run", help="本次运行名称，会和时间戳组成输出目录。")
    project.add_argument("--random-seed", type=int, default=20260703, help="随机种子，用于噪声和可复现实验。")

    road = parser.add_argument_group("road 道路参数组")
    road.add_argument("--road-width-m", type=float, default=18.0, help="道路横向宽度 W，单位 m。")
    road.add_argument("--road-length-m", type=float, default=120.0, help="道路沿 x 方向长度，单位 m。")
    road.add_argument("--road-surface-z-m", type=float, default=0.0, help="路面 z 坐标，单位 m；z 向下为正。")

    fiber = parser.add_argument_group("fiber 光纤参数组")
    fiber.add_argument("--fiber-y-m", type=float, default=0.0, help="光纤横向 y 坐标，典型单侧几何中近似为 0。")
    fiber.add_argument("--fiber-z-m", type=float, default=0.0, help="光纤等效接收深度，单位 m。")
    fiber.add_argument("--fiber-burial-depth-m", type=float, default=0.0, help="光纤埋深参数，默认 0；作为 receiver z 坐标的三维几何表达。")
    fiber.add_argument("--fiber-x-start-m", type=float, default=0.0, help="第一个 DAS-like 通道的 x 坐标，单位 m。")
    fiber.add_argument("--fiber-channel-spacing-m", type=float, default=1.0, help="相邻光纤通道间距，单位 m。")
    fiber.add_argument("--fiber-channel-count", type=int, default=121, help="光纤通道数量，是主参数。")
    fiber.add_argument("--receiver-geometry-mode", default="straight", choices=["straight", "polyline_csv"], help="接收几何模式：straight 为默认直线，polyline_csv 从 CSV 读取三维接收点。")
    fiber.add_argument("--receiver-polyline-csv", default=None, help="receiver polyline CSV 路径，列名建议为 x_m,y_m,z_m。")

    source = parser.add_argument_group("source 震源参数组")
    source.add_argument("--source-y-m", type=float, default=None, help="震源线 y 坐标；未设置时自动等于 road_width_m。")
    source.add_argument("--source-line-y-m", type=float, default=None, help="震源线 y 坐标别名；未设置时默认等于 road_width_m。")
    source.add_argument("--source-z-m", type=float, default=0.0, help="震源 z 坐标，单位 m。")
    source.add_argument("--source-x-start-m", type=float, default=10.0, help="第一个炮点的 x 坐标，单位 m。")
    source.add_argument("--source-shot-spacing-m", type=float, default=10.0, help="相邻炮点间距，单位 m。")
    source.add_argument("--source-shot-count", type=int, default=9, help="炮点数量，是主参数。")
    source.add_argument("--source-geometry-mode", default="line", choices=["line", "grid", "csv"], help="震源几何模式：line 默认直线，grid 为 x-y 网格，csv 从文件读取三维点。")
    source.add_argument("--source-points-csv", default=None, help="source points CSV 路径，列名建议为 x_m,y_m,z_m。")
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
    velocity.add_argument(
        "--velocity-model-type",
        default="layered",
        choices=[
            "uniform",
            "layered",
            "lateral_gradient",
            "localized_low_velocity_zone",
            "layered_with_anomaly_perturbation",
        ],
        help="Stage 5A 默认使用 layered；uniform 仅作为基线对比。",
    )
    velocity.add_argument("--rayleigh-velocity-mps", type=float, default=260.0, help="代表性等效瑞雷波速度，单位 m/s。")
    velocity.add_argument(
        "--layer-depths-m",
        default="0.3,1.0,3.0,8.0",
        help="分层模型各层底界深度，逗号分隔，单位 m。",
    )
    velocity.add_argument(
        "--layer-rayleigh-velocities-mps",
        default="120,180,260,350",
        help="分层模型各层等效 Rayleigh 速度，逗号分隔，单位 m/s。",
    )
    velocity.add_argument(
        "--lateral-gradient-x-mps-per-m",
        type=float,
        default=0.0,
        help="横向非均匀模型 x 方向速度梯度，单位 (m/s)/m。",
    )
    velocity.add_argument(
        "--lateral-gradient-y-mps-per-m",
        type=float,
        default=0.0,
        help="横向非均匀模型 y 方向速度梯度，单位 (m/s)/m。",
    )
    velocity.add_argument(
        "--low-velocity-zone-enabled",
        type=str_to_bool,
        default=False,
        help="是否启用局部低速区；localized_low_velocity_zone 类型下会参与走时。",
    )
    velocity.add_argument("--low-velocity-zone-x0-m", type=float, default=None, help="局部低速区中心 x；默认等于异常体 x0。")
    velocity.add_argument("--low-velocity-zone-y0-m", type=float, default=None, help="局部低速区中心 y；默认等于异常体 y0。")
    velocity.add_argument(
        "--low-velocity-zone-depth-m",
        type=float,
        default=None,
        help="局部低速区中心深度；默认等于异常体 depth。",
    )
    velocity.add_argument("--low-velocity-zone-radius-m", type=float, default=3.0, help="局部低速区半径，单位 m。")
    velocity.add_argument("--low-velocity-factor", type=float, default=0.7, help="低速区速度折减因子，0-1。")

    anomaly = parser.add_argument_group("anomaly 异常体参数组")
    anomaly.add_argument("--anomaly-type", default="cavity", choices=["cavity"], help="异常体类型；当前支持 cavity。")
    anomaly.add_argument("--anomaly-x0-m", type=float, default=60.0, help="异常体中心 x 坐标，单位 m。")
    anomaly.add_argument("--anomaly-y0-m", type=float, default=9.0, help="异常体中心 y 坐标，单位 m。")
    anomaly.add_argument("--anomaly-depth-m", type=float, default=3.0, help="异常体中心深度 h，单位 m，向下为正。")
    anomaly.add_argument("--anomaly-radius-m", type=float, default=1.5, help="异常体等效半径，单位 m。")
    anomaly.add_argument("--anomaly-shape", default="sphere", choices=["sphere", "ellipsoid", "box", "cylinder", "pipe_trench"], help="三维异常体形状，用于等效散射点生成。")
    anomaly.add_argument("--anomaly-size-x-m", type=float, default=2.0, help="异常体 x 方向尺度，单位 m。")
    anomaly.add_argument("--anomaly-size-y-m", type=float, default=2.0, help="异常体 y 方向尺度，单位 m。")
    anomaly.add_argument("--anomaly-size-z-m", type=float, default=1.0, help="异常体 z/depth 方向尺度，单位 m。")
    anomaly.add_argument("--anomaly-orientation-deg", type=float, default=0.0, help="异常体平面内朝向角，单位 degree。")
    anomaly.add_argument("--scatter-point-density", default="coarse", choices=["center", "coarse", "medium"], help="三维等效散射点密度。")
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
        help="DAS-like 响应层级；当前仍为点式接收近似。",
    )
    das_like.add_argument("--gauge-length-m", type=float, default=10.0, help="DAS gauge length 参数；point_receiver 不参与波形计算。")
    das_like.add_argument("--strain-rate", type=str_to_bool, default=False, help="应变率标签；当前仅进入 metadata。")

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
    output.add_argument("--output-prefix-style", default="compact", choices=["compact"], help="输出文件前缀规则，当前使用 compact。")
    output.add_argument(
        "--export-latest-stable",
        type=str_to_bool,
        default=True,
        help="full_pipeline 结束后是否导出 outputs/latest_stable 精选成果，便于人工快速检查。",
    )
    output.add_argument(
        "--latest-stable-dirname",
        default="latest_stable",
        help="稳定成果固定目录名，默认在 output_root_dir 下生成 outputs/latest_stable。",
    )
    output.add_argument(
        "--max-shot-figures",
        type=int,
        default=None,
        help="兼容 Stage 1 的旧参数；若设置，会覆盖 --max-shot-gather-figures。",
    )

    forward = parser.add_argument_group("forward 正演引擎参数组")
    forward.add_argument(
        "--forward-engine",
        default="layered_kinematic",
        choices=["kinematic_baseline", "layered_kinematic", "acoustic2d_prototype", "elastic2d_prototype"],
        help="正演引擎：layered_kinematic 为当前主线；acoustic2d/elastic2d prototype 仅作 validation。",
    )
    forward.add_argument("--acoustic2d-enabled", type=str_to_bool, default=False, help="是否运行 acoustic2d_prototype 验证输出。")
    forward.add_argument("--acoustic2d-nx", type=int, default=201, help="acoustic2d 网格 x 点数。")
    forward.add_argument("--acoustic2d-nz", type=int, default=101, help="acoustic2d 网格 z 点数。")
    forward.add_argument("--acoustic2d-dx-m", type=float, default=0.1, help="acoustic2d x 网格间距 m。")
    forward.add_argument("--acoustic2d-dz-m", type=float, default=0.1, help="acoustic2d z 网格间距 m。")
    forward.add_argument("--acoustic2d-duration-s", type=float, default=0.2, help="acoustic2d 模拟时长 s。")
    forward.add_argument("--acoustic2d-snapshot-count", type=int, default=6, help="acoustic2d 快照数量。")
    forward.add_argument("--elastic2d-enabled", type=str_to_bool, default=False, help="是否显式运行 elastic2d_prototype 验证输出。")
    forward.add_argument("--elastic2d-nx", type=int, default=201, help="elastic2d 网格 x 点数。")
    forward.add_argument("--elastic2d-nz", type=int, default=101, help="elastic2d 网格 z 点数。")
    forward.add_argument("--elastic2d-dx-m", type=float, default=0.1, help="elastic2d x 网格间距 m。")
    forward.add_argument("--elastic2d-dz-m", type=float, default=0.1, help="elastic2d z 网格间距 m。")
    forward.add_argument("--elastic2d-duration-s", type=float, default=0.25, help="elastic2d 模拟时长 s。")
    forward.add_argument("--elastic2d-snapshot-count", type=int, default=6, help="elastic2d 快照数量。")
    forward.add_argument("--elastic2d-vp-mps", type=float, default=500.0, help="elastic2d 均匀背景 Vp，单位 m/s。")
    forward.add_argument("--elastic2d-vs-mps", type=float, default=250.0, help="elastic2d 均匀背景 Vs，单位 m/s。")
    forward.add_argument("--elastic2d-rho-kgm3", type=float, default=1800.0, help="elastic2d 均匀背景密度，单位 kg/m3。")
    forward.add_argument("--elastic2d-void-enabled", type=str_to_bool, default=True, help="elastic2d 是否启用低速 void-like 扰动。")
    forward.add_argument("--elastic2d-void-x-m", type=float, default=None, help="elastic2d void-like 扰动中心 x；默认映射到局部网格内。")
    forward.add_argument("--elastic2d-void-z-m", type=float, default=None, help="elastic2d void-like 扰动中心 z；默认映射到局部网格内。")
    forward.add_argument("--elastic2d-void-radius-m", type=float, default=1.0, help="elastic2d void-like 扰动半径 m。")
    forward.add_argument("--elastic2d-void-vs-factor", type=float, default=0.2, help="elastic2d void-like 扰动 Vs 折减因子。")
    forward.add_argument("--elastic2d-void-vp-factor", type=float, default=0.5, help="elastic2d void-like 扰动 Vp 折减因子。")
    forward.add_argument("--elastic2d-void-rho-factor", type=float, default=0.5, help="elastic2d void-like 扰动密度折减因子。")
    forward.add_argument(
        "--elastic2d-source-type",
        default="vertical_force",
        choices=["vertical_force", "horizontal_force", "explosive"],
        help="elastic2d validation 震源类型；不影响 layered_kinematic 主定位 forward。",
    )
    forward.add_argument("--elastic2d-source-depth-m", type=float, default=0.2, help="elastic2d 震源深度 m。")
    forward.add_argument(
        "--elastic2d-rayleigh-pick-vmin-factor",
        type=float,
        default=0.7,
        help="Rayleigh-like 拾取速度下限，相对 Vs 的比例。",
    )
    forward.add_argument(
        "--elastic2d-rayleigh-pick-vmax-factor",
        type=float,
        default=1.1,
        help="Rayleigh-like 拾取速度上限，相对 Vs 的比例。",
    )
    forward.add_argument(
        "--elastic2d-sponge-strength-mode",
        default="medium",
        choices=["weak", "medium", "strong"],
        help="elastic2d sponge 吸收强度；仅用于 validation forward。",
    )
    forward.add_argument(
        "--elastic2d-free-surface-mode",
        default="approximate",
        choices=["approximate", "stress_zero_variant"],
        help="elastic2d 顶部自由表面近似模式；不是工业级自由表面格式。",
    )
    forward.add_argument(
        "--elastic2d-receiver-depth-index",
        default="surface",
        choices=["surface", "one_grid_below_surface"],
        help="elastic2d surface gather 接收深度；用于检查拾取是否误受表面数值点影响。",
    )

    scan = parser.add_argument_group("scan 扫描定位参数组")
    scan.add_argument("--scan-enabled", type=str_to_bool, default=True, help="是否启用基础 x-y-h 多炮扫描定位。")
    scan.add_argument("--scan-x-min-m", type=float, default=20.0, help="扫描 x 最小值，单位 m。")
    scan.add_argument("--scan-x-max-m", type=float, default=180.0, help="扫描 x 最大值，单位 m。")
    scan.add_argument("--scan-x-step-m", type=float, default=4.0, help="扫描 x 步长，单位 m；默认使用 Stage 4B 轻量三维 QC 网格。")
    scan.add_argument("--scan-y-min-m", type=float, default=2.0, help="扫描 y 最小值，单位 m。")
    scan.add_argument("--scan-y-max-m", type=float, default=18.0, help="扫描 y 最大值，单位 m。")
    scan.add_argument("--scan-y-step-m", type=float, default=2.0, help="扫描 y 步长，单位 m；需要更细定位时可通过命令行调小。")
    scan.add_argument("--scan-depth-min-m", type=float, default=0.5, help="扫描深度最小值，单位 m。")
    scan.add_argument("--scan-depth-max-m", type=float, default=8.0, help="扫描深度最大值，单位 m。")
    scan.add_argument("--scan-depth-step-m", type=float, default=1.0, help="扫描深度步长，单位 m；默认优先保证 full_pipeline 快速可跑。")
    scan.add_argument(
        "--score-method",
        default="diffraction_energy_stack",
        choices=["diffraction_energy_stack", "normalized_energy_stack"],
        help="扫描得分方法；normalized_energy_stack 会先按每道总能量归一化再叠加。",
    )
    scan.add_argument("--direct-mute-enabled", type=str_to_bool, default=True, help="扫描前是否按预测直达波时间窗 mute。")
    scan.add_argument(
        "--direct-mute-mode",
        default="taper",
        choices=["hard", "taper", "subtract", "none"],
        help="直达波压制模式：taper 为余弦平滑衰减，hard 为硬置零，none 不处理。",
    )
    scan.add_argument("--direct-mute-half-width-s", type=float, default=0.02, help="直达波 mute 半窗长，单位 s。")
    scan.add_argument("--scan-time-window-half-width-s", type=float, default=0.015, help="扫描能量拾取半窗长，单位 s。")
    scan.add_argument("--scan-use-depth-weight", type=str_to_bool, default=True, help="是否在扫描得分中加入 Rayleigh 波简化深度敏感性权重。")
    scan.add_argument("--rayleigh-penetration-factor", type=float, default=1.0, help="穿透深度系数：penetration_depth = factor * wavelength。")
    scan.add_argument("--active-score-kind", default="multi_attribute_unweighted", choices=["unweighted", "depth_weighted", "multi_attribute_unweighted"], help="主定位使用的 score 体；默认不让 depth prior 直接决定主结果。")
    scan.add_argument(
        "--compare-score-methods",
        type=str_to_bool,
        default=True,
        help="full_pipeline 中是否轻量对比 diffraction_energy_stack 与 normalized_energy_stack。",
    )
    scan.add_argument(
        "--score-method-list",
        default="diffraction_energy_stack,normalized_energy_stack",
        help="用于轻量对比的 score_method 列表，逗号分隔，必须来自 main.py 允许的扫描方法。",
    )
    scan.add_argument("--scan-score-mode", default="multi_attribute", choices=["energy", "multi_attribute"], help="定位评分模式：energy 为单属性能量，multi_attribute 为多属性加权组合。")
    scan.add_argument("--score-weight-energy", type=float, default=1.0, help="多属性 energy_score 权重。")
    scan.add_argument("--score-weight-normalized-energy", type=float, default=0.5, help="多属性 normalized_energy_score 权重。")
    scan.add_argument("--score-weight-matched-wavelet", type=float, default=1.0, help="多属性 matched_wavelet_score 权重。")
    scan.add_argument("--score-weight-semblance", type=float, default=0.5, help="多属性 semblance_score 权重。")
    scan.add_argument("--score-weight-frequency-shift", type=float, default=0.0, help="频移属性预留权重，本轮默认不参与。")
    scan.add_argument("--depth-prior-sensitivity-enabled", type=str_to_bool, default=True, help="是否输出 depth prior 强度轻量敏感性诊断。")
    scan.add_argument("--depth-prior-factor-list", default="0.5,1.0,2.0,off", help="depth prior 敏感性因子列表，逗号分隔，off 表示不加深度权重。")
    scan.add_argument(
        "--multi-attribute-ablation-enabled",
        type=str_to_bool,
        default=True,
        help="full_pipeline 中是否运行多属性评分消融实验。",
    )
    scan.add_argument(
        "--geometry-ablation-enabled",
        type=str_to_bool,
        default=True,
        help="full_pipeline 中是否运行三维观测几何消融实验。",
    )
    scan.add_argument(
        "--velocity-ablation-enabled",
        type=str_to_bool,
        default=True,
        help="full_pipeline 中是否运行 uniform/layered/heterogeneous 速度模型消融实验。",
    )

    preprocess = parser.add_argument_group("preprocessing 预处理参数组")
    preprocess.add_argument("--preprocess-enabled", type=str_to_bool, default=True, help="扫描前是否执行预处理流水线。")
    preprocess.add_argument("--bandpass-enabled", type=str_to_bool, default=True, help="是否执行带通滤波。")
    preprocess.add_argument("--bandpass-low-hz", type=float, default=5.0, help="带通低截止频率 Hz。")
    preprocess.add_argument("--bandpass-high-hz", type=float, default=80.0, help="带通高截止频率 Hz。")
    preprocess.add_argument("--agc-enabled", type=str_to_bool, default=False, help="是否执行 AGC。")
    preprocess.add_argument("--agc-window-s", type=float, default=0.05, help="AGC 滑动窗长度 s。")
    preprocess.add_argument("--envelope-enabled", type=str_to_bool, default=False, help="是否转为 Hilbert 包络属性。")
    preprocess.add_argument("--trace-normalization", default="rms", choices=["none", "rms", "max"], help="按道归一化方式。")
    preprocess.add_argument("--fk-filter-enabled", type=str_to_bool, default=False, help="是否执行简化 f-k 速度扇区滤波。")
    preprocess.add_argument("--fk-velocity-min-mps", type=float, default=80.0, help="f-k 速度扇区最小表观速度 m/s。")
    preprocess.add_argument("--fk-velocity-max-mps", type=float, default=500.0, help="f-k 速度扇区最大表观速度 m/s。")
    preprocess.add_argument(
        "--preprocessing-ablation-enabled",
        type=str_to_bool,
        default=True,
        help="full_pipeline 中是否运行预处理组合消融实验。",
    )

    task = parser.add_argument_group("task 任务控制参数组")
    task.add_argument("--wavelet-frequency-hz", type=float, default=35.0, help="Ricker 子波主频，单位 Hz。")
    task.add_argument("--wavelet-dominant-frequency-hz", type=float, default=30.0, help="用于 Rayleigh 波深度敏感性估计的主频，单位 Hz。")

    confidence = parser.add_argument_group("confidence 基础置信度诊断参数组")
    confidence.add_argument(
        "--confidence-threshold-ratio",
        type=float,
        default=0.9,
        help="高分区阈值比例，例如 0.9 表示统计 >=0.9*best_score 的候选点。",
    )
    confidence.add_argument(
        "--confidence-neighborhood-radius",
        type=int,
        default=1,
        help="peak sharpness 局部邻域半径，单位为扫描网格索引。",
    )
    confidence.add_argument(
        "--consistency-warning-cv-threshold",
        type=float,
        default=0.8,
        help="多炮贡献变异系数超过该值时提示一致性较差。",
    )
    confidence.add_argument(
        "--coupling-warning-span-y-m",
        type=float,
        default=4.0,
        help="高分区 y 方向跨度超过该阈值时，参与 y-depth 耦合风险判断，单位 m。",
    )
    confidence.add_argument(
        "--coupling-warning-span-depth-m",
        type=float,
        default=2.0,
        help="高分区 depth 方向跨度超过该阈值时，参与 y-depth 耦合风险判断，单位 m。",
    )
    confidence.add_argument(
        "--raw-weighted-depth-diff-warning-m",
        type=float,
        default=1.0,
        help="raw_best_depth 与 weighted_best_depth 差异超过该阈值时触发深度先验偏置警告，单位 m。",
    )
    confidence.add_argument(
        "--raw-weighted-location-diff-warning-m",
        type=float,
        default=2.0,
        help="raw_best 与 weighted_best 三维距离差异超过该阈值时触发 raw/weighted 分歧警告，单位 m。",
    )

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
            z_m=args.fiber_burial_depth_m if args.fiber_burial_depth_m is not None else args.fiber_z_m,
            burial_depth_m=args.fiber_burial_depth_m,
            x_start_m=args.fiber_x_start_m,
            channel_spacing_m=args.fiber_channel_spacing_m,
            channel_count=args.fiber_channel_count,
            geometry_mode=args.receiver_geometry_mode,
            polyline_csv=args.receiver_polyline_csv,
        ),
        source=_namespace(
            y_m=args.source_y_m if args.source_y_m is not None else args.source_line_y_m,
            line_y_m=args.source_line_y_m,
            z_m=args.source_z_m,
            x_start_m=args.source_x_start_m,
            shot_spacing_m=args.source_shot_spacing_m,
            shot_count=args.source_shot_count,
            source_type=args.source_type,
            geometry_mode=args.source_geometry_mode,
            points_csv=args.source_points_csv,
        ),
        time=_namespace(dt_s=args.time_dt_s, record_length_s=args.time_record_length_s, t0_s=args.time_t0_s),
        velocity=_namespace(
            model_type=args.velocity_model_type,
            rayleigh_velocity_mps=args.rayleigh_velocity_mps,
            layer_depths_m=[float(item.strip()) for item in args.layer_depths_m.split(",") if item.strip()],
            layer_rayleigh_velocities_mps=[
                float(item.strip()) for item in args.layer_rayleigh_velocities_mps.split(",") if item.strip()
            ],
            lateral_gradient_x_mps_per_m=args.lateral_gradient_x_mps_per_m,
            lateral_gradient_y_mps_per_m=args.lateral_gradient_y_mps_per_m,
            low_velocity_zone_enabled=args.low_velocity_zone_enabled,
            low_velocity_zone_x0_m=args.low_velocity_zone_x0_m
            if args.low_velocity_zone_x0_m is not None
            else args.anomaly_x0_m,
            low_velocity_zone_y0_m=args.low_velocity_zone_y0_m
            if args.low_velocity_zone_y0_m is not None
            else args.anomaly_y0_m,
            low_velocity_zone_depth_m=args.low_velocity_zone_depth_m
            if args.low_velocity_zone_depth_m is not None
            else args.anomaly_depth_m,
            low_velocity_zone_radius_m=args.low_velocity_zone_radius_m,
            low_velocity_factor=args.low_velocity_factor,
        ),
        anomaly=_namespace(
            anomaly_type=args.anomaly_type,
            x0_m=args.anomaly_x0_m,
            y0_m=args.anomaly_y0_m,
            depth_m=args.anomaly_depth_m,
            radius_m=args.anomaly_radius_m,
            shape=args.anomaly_shape,
            size_x_m=args.anomaly_size_x_m,
            size_y_m=args.anomaly_size_y_m,
            size_z_m=args.anomaly_size_z_m,
            orientation_deg=args.anomaly_orientation_deg,
            scatter_point_density=args.scatter_point_density,
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
            export_latest_stable=args.export_latest_stable,
            latest_stable_dirname=args.latest_stable_dirname,
        ),
        forward=_namespace(
            engine=args.forward_engine,
            acoustic2d_enabled=args.acoustic2d_enabled,
            acoustic2d_nx=args.acoustic2d_nx,
            acoustic2d_nz=args.acoustic2d_nz,
            acoustic2d_dx_m=args.acoustic2d_dx_m,
            acoustic2d_dz_m=args.acoustic2d_dz_m,
            acoustic2d_duration_s=args.acoustic2d_duration_s,
            acoustic2d_snapshot_count=args.acoustic2d_snapshot_count,
            elastic2d_enabled=args.elastic2d_enabled,
            elastic2d_nx=args.elastic2d_nx,
            elastic2d_nz=args.elastic2d_nz,
            elastic2d_dx_m=args.elastic2d_dx_m,
            elastic2d_dz_m=args.elastic2d_dz_m,
            elastic2d_duration_s=args.elastic2d_duration_s,
            elastic2d_snapshot_count=args.elastic2d_snapshot_count,
            elastic2d_vp_mps=args.elastic2d_vp_mps,
            elastic2d_vs_mps=args.elastic2d_vs_mps,
            elastic2d_rho_kgm3=args.elastic2d_rho_kgm3,
            elastic2d_void_enabled=args.elastic2d_void_enabled,
            elastic2d_void_x_m=args.elastic2d_void_x_m,
            elastic2d_void_z_m=args.elastic2d_void_z_m,
            elastic2d_void_radius_m=args.elastic2d_void_radius_m,
            elastic2d_void_vs_factor=args.elastic2d_void_vs_factor,
            elastic2d_void_vp_factor=args.elastic2d_void_vp_factor,
            elastic2d_void_rho_factor=args.elastic2d_void_rho_factor,
            elastic2d_source_type=args.elastic2d_source_type,
            elastic2d_source_depth_m=args.elastic2d_source_depth_m,
            elastic2d_rayleigh_pick_vmin_factor=args.elastic2d_rayleigh_pick_vmin_factor,
            elastic2d_rayleigh_pick_vmax_factor=args.elastic2d_rayleigh_pick_vmax_factor,
            elastic2d_sponge_strength_mode=args.elastic2d_sponge_strength_mode,
            elastic2d_free_surface_mode=args.elastic2d_free_surface_mode,
            elastic2d_receiver_depth_index=args.elastic2d_receiver_depth_index,
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
            direct_mute_mode=args.direct_mute_mode,
            direct_mute_half_width_s=args.direct_mute_half_width_s,
            time_window_half_width_s=args.scan_time_window_half_width_s,
            use_depth_weight=args.scan_use_depth_weight,
            rayleigh_penetration_factor=args.rayleigh_penetration_factor,
            active_score_kind=args.active_score_kind,
            compare_score_methods=args.compare_score_methods,
            score_method_list=[item.strip() for item in args.score_method_list.split(",") if item.strip()],
            score_mode=args.scan_score_mode,
            weight_energy=args.score_weight_energy,
            weight_normalized_energy=args.score_weight_normalized_energy,
            weight_matched_wavelet=args.score_weight_matched_wavelet,
            weight_semblance=args.score_weight_semblance,
            weight_frequency_shift=args.score_weight_frequency_shift,
            depth_prior_sensitivity_enabled=args.depth_prior_sensitivity_enabled,
            depth_prior_factor_list=[item.strip() for item in args.depth_prior_factor_list.split(",") if item.strip()],
            multi_attribute_ablation_enabled=args.multi_attribute_ablation_enabled,
            geometry_ablation_enabled=args.geometry_ablation_enabled,
            velocity_ablation_enabled=args.velocity_ablation_enabled,
        ),
        preprocessing=_namespace(
            enabled=args.preprocess_enabled,
            bandpass_enabled=args.bandpass_enabled,
            bandpass_low_hz=args.bandpass_low_hz,
            bandpass_high_hz=args.bandpass_high_hz,
            agc_enabled=args.agc_enabled,
            agc_window_s=args.agc_window_s,
            envelope_enabled=args.envelope_enabled,
            trace_normalization=args.trace_normalization,
            fk_filter_enabled=args.fk_filter_enabled,
            fk_velocity_min_mps=args.fk_velocity_min_mps,
            fk_velocity_max_mps=args.fk_velocity_max_mps,
            ablation_enabled=args.preprocessing_ablation_enabled,
        ),
        task=_namespace(
            wavelet_frequency_hz=args.wavelet_frequency_hz,
            wavelet_dominant_frequency_hz=args.wavelet_dominant_frequency_hz,
        ),
        confidence=_namespace(
            threshold_ratio=args.confidence_threshold_ratio,
            neighborhood_radius=args.confidence_neighborhood_radius,
            consistency_warning_cv_threshold=args.consistency_warning_cv_threshold,
            coupling_warning_span_y_m=args.coupling_warning_span_y_m,
            coupling_warning_span_depth_m=args.coupling_warning_span_depth_m,
            raw_weighted_depth_diff_warning_m=args.raw_weighted_depth_diff_warning_m,
            raw_weighted_location_diff_warning_m=args.raw_weighted_location_diff_warning_m,
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
    if len(params.velocity.layer_depths_m) != len(params.velocity.layer_rayleigh_velocities_mps):
        raise ValueError(
            "layer_depths_m 与 layer_rayleigh_velocities_mps 错误：二者数量必须一致，"
            f"当前分别为 {len(params.velocity.layer_depths_m)} 和 {len(params.velocity.layer_rayleigh_velocities_mps)}。"
        )
    if len(params.velocity.layer_depths_m) < 1:
        raise ValueError("layer_depths_m 错误：至少需要一层速度。")
    if any(value <= 0 for value in params.velocity.layer_depths_m):
        raise ValueError(f"layer_depths_m 错误：当前值为 {params.velocity.layer_depths_m}，所有层底深度必须 > 0。")
    if any(
        params.velocity.layer_depths_m[index] <= params.velocity.layer_depths_m[index - 1]
        for index in range(1, len(params.velocity.layer_depths_m))
    ):
        raise ValueError(f"layer_depths_m 错误：当前值为 {params.velocity.layer_depths_m}，必须严格递增。")
    if any(value <= 0 for value in params.velocity.layer_rayleigh_velocities_mps):
        raise ValueError(
            "layer_rayleigh_velocities_mps 错误："
            f"当前值为 {params.velocity.layer_rayleigh_velocities_mps}，所有速度必须 > 0。"
        )
    if params.velocity.low_velocity_zone_radius_m <= 0:
        raise ValueError(
            f"low_velocity_zone_radius_m 错误：当前值为 {params.velocity.low_velocity_zone_radius_m}，合理条件是 > 0。"
        )
    if not (0.05 <= params.velocity.low_velocity_factor <= 1.0):
        raise ValueError(
            f"low_velocity_factor 错误：当前值为 {params.velocity.low_velocity_factor}，合理条件是 0.05 <= factor <= 1.0。"
        )
    if params.anomaly.depth_m <= 0:
        raise ValueError(f"anomaly_depth_m 错误：当前值为 {params.anomaly.depth_m}，合理条件是异常体深度 > 0。")
    if params.anomaly.size_x_m <= 0 or params.anomaly.size_y_m <= 0 or params.anomaly.size_z_m <= 0:
        raise ValueError(
            "anomaly size 参数错误："
            f"当前为 ({params.anomaly.size_x_m}, {params.anomaly.size_y_m}, {params.anomaly.size_z_m})，合理条件是三方向尺度均 > 0。"
        )
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
    if params.forward.engine in {"acoustic2d_prototype", "elastic2d_prototype"} and params.project.task in {
        "debug",
        "forward",
        "full_pipeline",
    }:
        raise ValueError("acoustic2d/elastic2d prototype 是 validation 引擎，不能作为默认 DAS-like 主流程 forward_engine。")
    if params.forward.acoustic2d_nx < 20 or params.forward.acoustic2d_nz < 20:
        raise ValueError("acoustic2d_nx/acoustic2d_nz 错误：最小网格点数均应 >= 20。")
    if params.forward.acoustic2d_dx_m <= 0 or params.forward.acoustic2d_dz_m <= 0:
        raise ValueError("acoustic2d dx/dz 错误：网格间距必须 > 0。")
    if params.forward.acoustic2d_duration_s <= 0:
        raise ValueError("acoustic2d_duration_s 错误：模拟时长必须 > 0。")
    if params.forward.acoustic2d_snapshot_count < 1:
        raise ValueError("acoustic2d_snapshot_count 错误：快照数量必须 >= 1。")
    if params.forward.elastic2d_nx < 20 or params.forward.elastic2d_nz < 20:
        raise ValueError("elastic2d_nx/elastic2d_nz 错误：最小网格点数均应 >= 20。")
    if params.forward.elastic2d_dx_m <= 0 or params.forward.elastic2d_dz_m <= 0:
        raise ValueError("elastic2d dx/dz 错误：网格间距必须 > 0。")
    if params.forward.elastic2d_duration_s <= 0:
        raise ValueError("elastic2d_duration_s 错误：模拟时长必须 > 0。")
    if params.forward.elastic2d_snapshot_count < 1:
        raise ValueError("elastic2d_snapshot_count 错误：快照数量必须 >= 1。")
    if params.forward.elastic2d_vp_mps <= 0 or params.forward.elastic2d_vs_mps <= 0:
        raise ValueError("elastic2d Vp/Vs 错误：速度必须 > 0。")
    if params.forward.elastic2d_vp_mps <= params.forward.elastic2d_vs_mps:
        raise ValueError("elastic2d Vp/Vs 错误：Vp 应大于 Vs。")
    if params.forward.elastic2d_rho_kgm3 <= 0:
        raise ValueError("elastic2d rho 错误：密度必须 > 0。")
    if params.forward.elastic2d_void_radius_m <= 0:
        raise ValueError("elastic2d void radius 错误：半径必须 > 0。")
    for name, value in {
        "elastic2d_void_vs_factor": params.forward.elastic2d_void_vs_factor,
        "elastic2d_void_vp_factor": params.forward.elastic2d_void_vp_factor,
        "elastic2d_void_rho_factor": params.forward.elastic2d_void_rho_factor,
    }.items():
        if not (0.0 < value <= 1.0):
            raise ValueError(f"{name} 错误：折减因子必须在 (0, 1]。")
    if params.forward.elastic2d_source_depth_m < 0:
        raise ValueError("elastic2d_source_depth_m 错误：震源深度必须 >= 0。")
    if params.forward.elastic2d_rayleigh_pick_vmin_factor <= 0:
        raise ValueError("elastic2d_rayleigh_pick_vmin_factor 错误：必须 > 0。")
    if params.forward.elastic2d_rayleigh_pick_vmax_factor <= params.forward.elastic2d_rayleigh_pick_vmin_factor:
        raise ValueError("elastic2d Rayleigh pick 速度范围错误：vmax factor 必须大于 vmin factor。")
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
    if not params.output.latest_stable_dirname.strip():
        raise ValueError("latest_stable_dirname 错误：目录名不能为空。")
    if "/" in params.output.latest_stable_dirname or "\\" in params.output.latest_stable_dirname:
        raise ValueError(
            f"latest_stable_dirname 错误：当前值为 {params.output.latest_stable_dirname}，合理条件是不包含路径分隔符。"
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
    allowed_score_methods = {"diffraction_energy_stack", "normalized_energy_stack"}
    if not params.scan.score_method_list:
        raise ValueError("score_method_list 错误：至少需要包含一个 score method。")
    invalid_methods = [method for method in params.scan.score_method_list if method not in allowed_score_methods]
    if invalid_methods:
        raise ValueError(
            f"score_method_list 错误：包含不支持的方法 {invalid_methods}，合理选项是 {sorted(allowed_score_methods)}。"
        )
    if params.fiber.geometry_mode == "polyline_csv" and not params.fiber.polyline_csv:
        raise ValueError("receiver_polyline_csv 错误：receiver-geometry-mode=polyline_csv 时必须提供 CSV 路径。")
    if params.source.geometry_mode == "csv" and not params.source.points_csv:
        raise ValueError("source_points_csv 错误：source-geometry-mode=csv 时必须提供 CSV 路径。")
    if params.preprocessing.bandpass_low_hz <= 0 or params.preprocessing.bandpass_high_hz <= 0:
        raise ValueError("bandpass 频率错误：low/high 均必须 > 0。")
    if params.preprocessing.bandpass_low_hz >= params.preprocessing.bandpass_high_hz:
        raise ValueError(
            f"bandpass 频率错误：low={params.preprocessing.bandpass_low_hz}, high={params.preprocessing.bandpass_high_hz}，合理条件是 low < high。"
        )
    if params.preprocessing.agc_window_s <= 0:
        raise ValueError(f"agc_window_s 错误：当前值为 {params.preprocessing.agc_window_s}，合理条件是 > 0。")
    if params.preprocessing.fk_velocity_min_mps <= 0 or params.preprocessing.fk_velocity_max_mps <= 0:
        raise ValueError("fk velocity 错误：速度上下限均必须 > 0。")
    if params.preprocessing.fk_velocity_min_mps >= params.preprocessing.fk_velocity_max_mps:
        raise ValueError("fk velocity 错误：fk_velocity_min_mps 必须小于 fk_velocity_max_mps。")
    if min(
        params.scan.weight_energy,
        params.scan.weight_normalized_energy,
        params.scan.weight_matched_wavelet,
        params.scan.weight_semblance,
        params.scan.weight_frequency_shift,
    ) < 0:
        raise ValueError("score weight 错误：多属性评分权重不能为负。")
    if not params.scan.depth_prior_factor_list:
        raise ValueError("depth_prior_factor_list 错误：至少需要一个因子或 off。")
    if params.task.wavelet_frequency_hz <= 0:
        raise ValueError(f"wavelet_frequency_hz 错误：当前值为 {params.task.wavelet_frequency_hz}，合理条件是 > 0。")
    if params.task.wavelet_dominant_frequency_hz <= 0:
        raise ValueError(
            f"wavelet_dominant_frequency_hz 错误：当前值为 {params.task.wavelet_dominant_frequency_hz}，合理条件是 > 0。"
        )
    if not (0.0 < params.confidence.threshold_ratio <= 1.0):
        raise ValueError(
            f"confidence_threshold_ratio 错误：当前值为 {params.confidence.threshold_ratio}，合理条件是 0 < ratio <= 1。"
        )
    if params.confidence.neighborhood_radius < 0:
        raise ValueError(
            f"confidence_neighborhood_radius 错误：当前值为 {params.confidence.neighborhood_radius}，合理条件是 >= 0。"
        )
    if params.confidence.consistency_warning_cv_threshold <= 0:
        raise ValueError(
            "consistency_warning_cv_threshold 错误："
            f"当前值为 {params.confidence.consistency_warning_cv_threshold}，合理条件是 > 0。"
        )
    if params.confidence.coupling_warning_span_y_m <= 0:
        raise ValueError(
            f"coupling_warning_span_y_m 错误：当前值为 {params.confidence.coupling_warning_span_y_m}，合理条件是 > 0。"
        )
    if params.confidence.coupling_warning_span_depth_m <= 0:
        raise ValueError(
            "coupling_warning_span_depth_m 错误："
            f"当前值为 {params.confidence.coupling_warning_span_depth_m}，合理条件是 > 0。"
        )
    if params.confidence.raw_weighted_depth_diff_warning_m <= 0:
        raise ValueError(
            "raw_weighted_depth_diff_warning_m 错误："
            f"当前值为 {params.confidence.raw_weighted_depth_diff_warning_m}，合理条件是 > 0。"
        )
    if params.confidence.raw_weighted_location_diff_warning_m <= 0:
        raise ValueError(
            "raw_weighted_location_diff_warning_m 错误："
            f"当前值为 {params.confidence.raw_weighted_location_diff_warning_m}，合理条件是 > 0。"
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
    params.derived.latest_stable_dir = str(Path(params.output.root_dir) / params.output.latest_stable_dirname)

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

    print("=== hcz_void_plus Stage 5F 参数摘要 ===")
    print(f"task: {params.project.task}")
    print(f"run_name: {params.project.run_name}")
    print(f"road width/length: {params.road.width_m} m / {params.road.length_m} m")
    print(f"fiber channels: {params.fiber.channel_count}, x=[{params.fiber.x_start_m}, {params.derived.fiber_x_end_m}] m")
    print(f"shots: {params.source.shot_count}, source_y={params.source.y_m} m")
    print(f"time: nt={params.derived.nt}, dt={params.time.dt_s} s")
    print(f"scan grid: {params.derived.scan_shape}, points={params.derived.scan_grid_point_count}")
    print(f"forward engine: {params.forward.engine}")
    print(f"velocity model: {params.velocity.model_type}")
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
    raise ValueError(f"task={params.project.task} 已预留，但当前阶段尚未实现该独立流程。")


def main(argv: Iterable[str] | None = None) -> dict[str, Any]:
    """命令行总入口。"""

    args = parse_arguments(argv)
    params = args_to_params(args)
    return dispatch_task(params)


if __name__ == "__main__":
    main()
