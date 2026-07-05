"""Stage 4B 验证报告生成。"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _location_text(item: dict[str, Any]) -> str:
    loc = item.get("best_location") or item.get("recommended_location") or {}
    err = item.get("truth_error", {})
    return (
        f"x={loc.get('x_m')}, y={loc.get('y_m')}, h={loc.get('depth_m')}, "
        f"error={err.get('distance_m')}"
    )


def write_preprocessing_ablation_report(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# 预处理消融验证报告",
        "",
        "本报告比较不同预处理组合对三维运动学扫描的影响。消融使用轻量三维诊断网格，不是大规模鲁棒性扫描。",
        "",
        "| case | best | y_span_m | depth_span_m | diffraction_ratio | direct_residual | flag |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for name, item in result["cases"].items():
        lines.append(
            "| "
            f"{name} | {_location_text(item)} | {item['y_span_m']:.4g} | {item['depth_span_m']:.4g} | "
            f"{item['diffraction_curve_energy_ratio']:.4g} | {item['direct_wave_residual_ratio']:.4g} | "
            f"{item['low_confidence_flag']} |"
        )
    lines.extend(
        [
            "",
            "## 结论",
            "",
            f"- 最小真值误差组合：`{result['best_truth_error_case']}`。",
            f"- y/depth 跨度最小组合：`{result['narrowest_y_depth_case']}`。",
            "- 若某组合降低 direct_residual 但同时降低 diffraction_ratio，应视为可能误伤有效绕射。",
            "- 当前仍是 kinematic approximation 与 DAS-like response approximation，不能作为工程确诊。",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_fk_filter_validation_report(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# FK / f-v 滤波验证报告",
        "",
        "当前 FK 滤波是简化速度扇区 QC，不是成熟面波 FK 分离软件。",
        "",
        f"- strict FK applicable: `{result['applicable_as_strict_fk']}`",
        f"- warning: {result.get('warning') or '无'}",
        f"- direct wave reduction ratio: `{result['direct_wave_reduction_ratio']:.4g}`",
        f"- diffraction preservation ratio: `{result['diffraction_preservation_ratio']:.4g}`",
        f"- shape preserved: `{result['shape_preserved']}`",
        "",
        "## 解释",
        "",
        "- direct wave reduction ratio 越高，说明直达波局部能量削弱越明显。",
        "- diffraction preservation ratio 接近或大于 1，说明理论绕射曲线附近能量没有被明显误伤。",
        "- receiver 不是 straight 或通道非均匀时，f-k 解释只能作为近似 QC。",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_attribute_validation_report(path: Path, title: str, summary: dict[str, Any], note: str) -> None:
    lines = [
        f"# {title}",
        "",
        f"- best: {_location_text(summary)}",
        f"- y_span_m: `{summary.get('y_span_m')}`",
        f"- depth_span_m: `{summary.get('depth_span_m')}`",
        f"- high_score_component_count: `{summary.get('high_score_component_count')}`",
        f"- multi_region_warning: `{summary.get('multi_region_warning')}`",
        "",
        note,
        "",
        "该属性仍是运动学 DAS-like 数据上的科研诊断，不是工程确诊。",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_multi_attribute_ablation_report(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# 多属性评分消融报告",
        "",
        "| group | best | y_span_m | depth_span_m | components | flag |",
        "|---|---|---:|---:|---:|---|",
    ]
    for name, item in result["groups"].items():
        lines.append(
            "| "
            f"{name} | {_location_text(item)} | {item['y_span_m']:.4g} | {item['depth_span_m']:.4g} | "
            f"{item['high_score_component_count']} | {item['low_confidence_flag']} |"
        )
    lines.extend(
        [
            "",
            f"- best_group_by_truth_error: `{result.get('best_group_by_truth_error')}`",
            f"- full_multi_attribute_improved_over_energy: `{result.get('multi_attribute_improved_over_energy')}`",
            "",
            result.get("note", ""),
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_geometry_ablation_report(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# 三维几何消融报告",
        "",
        "每个案例都重新合成运动学 DAS-like 数据，并在三维诊断网格上扫描。",
        "",
        "| geometry case | best | y_span_m | depth_span_m | source_y_span_m | receiver_y_span_m | flag |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for name, item in result["cases"].items():
        lines.append(
            "| "
            f"{name} | {_location_text(item)} | {item['y_span_m']:.4g} | {item['depth_span_m']:.4g} | "
            f"{item['source_y_span_m']:.4g} | {item['receiver_y_span_m']:.4g} | {item['low_confidence_flag']} |"
        )
    lines.extend(
        [
            "",
            f"- y 方向跨度改善最明显：`{result['best_y_resolution_case']}`。",
            f"- depth 稳定性最好：`{result['best_depth_stability_case']}`。",
            f"- 真值误差最小：`{result['best_truth_error_case']}`。",
            "",
            "若非共线或双侧震源明显缩小 y/depth 跨度，说明当前场景更应优先增加震源方位覆盖，而不是只调 score。",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_velocity_model_ablation_report(path: Path, result: dict[str, Any]) -> None:
    """写出速度模型消融报告。

    报告重点不是宣布某个模型“真实”，而是说明分层/非均匀运动学速度如何改变
    绕射走时、定位误差和三维高分区跨度。
    """

    lines = [
        "# 速度模型消融报告",
        "",
        "本报告比较 uniform、layered、lateral gradient、localized low velocity zone 等等效 Rayleigh 速度模型。",
        "所有结果仍是 straight-ray kinematic approximation，不是 3D elastic wavefield。",
        "",
        "| velocity model | best | error_m | y_span_m | depth_span_m | residual_rms_ms | flag |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for name, item in result["cases"].items():
        lines.append(
            "| "
            f"{name} | {_location_text(item)} | {item['truth_error']['distance_m']:.4g} | "
            f"{item['y_span_m']:.4g} | {item['depth_span_m']:.4g} | "
            f"{1000.0 * item['travel_time_residual_to_uniform_rms_s']:.4g} | {item['confidence_flag']} |"
        )
    lines.extend(
        [
            "",
            "## 结论",
            "",
            f"- 真值误差最小模型：`{result['best_truth_error_case']}`。",
            f"- 深度误差最小模型：`{result['best_depth_case']}`。",
            f"- 相对 uniform 走时残差最大模型：`{result['largest_travel_time_residual_case']}`。",
            "- 如果 layered 与 uniform 的走时残差不可忽略，真实数据反演不应继续只依赖 uniform 速度。",
            "- 局部低速带可能导致定位偏移，也可能被误解释为空洞响应，因此必须在报告中作为风险列出。",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_model_mismatch_report(path: Path, result: dict[str, Any]) -> None:
    """写出正演/扫描速度模型错配报告。"""

    lines = [
        "# 正演模型与扫描模型错配报告",
        "",
        "真实道路介质与反演速度假设通常不一致。本报告用轻量三维运动学实验检查这种错配对定位的影响。",
        "",
        "| case | forward model | scan model | best | error_m | y_span_m | depth_span_m | flag |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for name, item in result["cases"].items():
        lines.append(
            "| "
            f"{name} | {item['forward_model_type']} | {item['scan_model_type']} | {_location_text(item)} | "
            f"{item['truth_error']['distance_m']:.4g} | {item['y_span_m']:.4g} | "
            f"{item['depth_span_m']:.4g} | {item['low_confidence_flag']} |"
        )
    lines.extend(
        [
            "",
            "## 风险解释",
            "",
            f"- 误差最小案例：`{result['safest_case']}`。",
            f"- 误差最大案例：`{result['riskiest_case']}`。",
            f"- 当前最低推荐速度模型：`{result['minimum_recommended_velocity_model']}`。",
            "- 如果真实为 layered 但扫描仍用 uniform，depth 与 y-depth 耦合可能出现系统偏差。",
            "- 本报告只用于科研算法风险诊断，不能作为工程确诊或速度结构反演结论。",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_forward_engine_ablation_report(path: Path, result: dict[str, Any]) -> None:
    """写出 Stage 5B 正演引擎消融报告。

    报告强调 F0/F1/F2 的角色差异：F1 是当前主定位 forward，F2 只验证声学
    波动方程基础设施，不能被解释为 Rayleigh 波或空洞弹性散射正演。
    """

    layered_vs_baseline = result["layered_vs_baseline"]
    lines = [
        "# 正演引擎消融报告",
        "",
        "本报告比较 `kinematic_baseline`、`layered_kinematic` 与 `acoustic2d_prototype` 的阶段角色。",
        "`acoustic2d_prototype` 只验证波动方程数值框架，不参与 DAS-like 主定位，也不能代表 Rayleigh 波正演。",
        "",
        "| engine | stage | velocity/model | data/snapshot shape | RMS or max amplitude | role |",
        "|---|---|---|---|---:|---|",
    ]
    baseline = result["engines"]["kinematic_baseline"]
    layered = result["engines"]["layered_kinematic"]
    acoustic = result["engines"]["acoustic2d_prototype"]
    lines.extend(
        [
            "| "
            f"kinematic_baseline | {baseline['forward_stage']} | {baseline['velocity_model_type']} | "
            f"{baseline['data_shape']} | {baseline['synthetic_rms']:.4g} | F0 快速基线 |",
            "| "
            f"layered_kinematic | {layered['forward_stage']} | {layered['velocity_model_type']} | "
            f"{layered['data_shape']} | {layered['synthetic_rms']:.4g} | F1 当前主线 |",
            "| "
            f"acoustic2d_prototype | {acoustic['forward_stage']} | scalar acoustic | "
            f"{acoustic['shot_gather_shape']} / {acoustic['wavefield_snapshot_shape']} | "
            f"{acoustic['max_abs_amplitude']:.4g} | F2 validation prototype |",
        ]
    )
    lines.extend(
        [
            "",
            "## F1 相对 F0 的差异",
            "",
            f"- synthetic RMS difference：`{layered_vs_baseline['synthetic_rms_difference']:.4g}`。",
            f"- synthetic relative difference：`{layered_vs_baseline['synthetic_relative_difference']:.4g}`。",
            f"- travel-time residual mean：`{layered_vs_baseline['travel_time_residual_mean_ms']:.4g}` ms。",
            f"- travel-time residual RMS：`{layered_vs_baseline['travel_time_residual_rms_ms']:.4g}` ms。",
            f"- travel-time residual max abs：`{layered_vs_baseline['travel_time_residual_max_abs_ms']:.4g}` ms。",
            "",
            "## acoustic2d prototype 边界",
            "",
            f"- CFL stable：`{acoustic['cfl_stable']}`。",
            f"- CFL number：`{acoustic['cfl_number']:.4g}`。",
            "- acoustic2d 只有标量声学压力场，没有剪切波和自由表面 Rayleigh 模式。",
            "- acoustic2d 可以验证网格、震源、接收、absorbing boundary、CFL 和快照输出。",
            "- acoustic2d 不能验证 Rayleigh/free-surface/void scattering；下一步必须进入 elastic2d。",
            "",
            "## 当前结论",
            "",
            "- active forward engine：`layered_kinematic`。",
            "- available forward engines：`kinematic_baseline, layered_kinematic, acoustic2d_prototype`。",
            "- next required forward：`elastic2d`。",
            "- 当前结果仍是科研候选区，不是工程确诊。",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_acoustic2d_prototype_report(path: Path, result: dict[str, Any]) -> None:
    """写出 acoustic2d prototype 专项报告。"""

    acoustic = result["engines"]["acoustic2d_prototype"]
    lines = [
        "# acoustic2d prototype 验证报告",
        "",
        "`acoustic2d_prototype` 是二维标量 acoustic FDTD 最小原型。它只用于验证波动方程基础设施，不能代表 Rayleigh 波、自由表面或空洞弹性散射正演。",
        "",
        "## 输出",
        "",
        f"- shot gather shape：`{acoustic['shot_gather_shape']}`。",
        f"- wavefield snapshot shape：`{acoustic['wavefield_snapshot_shape']}`。",
        f"- snapshot count：`{acoustic['snapshot_count']}`。",
        f"- CFL stable：`{acoustic['cfl_stable']}`。",
        f"- CFL number：`{acoustic['cfl_number']:.4g}`。",
        f"- max abs amplitude：`{acoustic['max_abs_amplitude']:.4g}`。",
        f"- energy：`{acoustic['energy']:.4g}`。",
        "",
        "## 能验证什么",
        "",
        "- 二维网格和分层 acoustic velocity 的组织方式。",
        "- Ricker 震源、接收线和 shot gather 输出。",
        "- sponge absorbing boundary 与 CFL 稳定性检查。",
        "- wavefield snapshots 的保存和可视化链路。",
        "",
        "## 不能验证什么",
        "",
        "- 不能验证 Rayleigh 波。",
        "- 不能验证自由表面条件。",
        "- 不能验证 void/free-surface/elastic scattering。",
        "- 不能替代 `layered_kinematic` 主流程，也不能替代下一步 `elastic2d`。",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_elastic2d_rayleigh_validation_report(path: Path, result: dict[str, Any]) -> None:
    """写出 elastic2d Rayleigh-like sanity check 报告。"""

    lines = [
        "# elastic2d Rayleigh/free-surface 验证报告",
        "",
        "本报告基于最小 collocated-grid velocity-stress elastic2d prototype。它是局部物理验证起点，不是工业级 elastic 模拟。",
        "",
        f"- CFL stable：`{result['cfl_info']['stable']}`。",
        f"- CFL number：`{result['cfl_info']['cfl_number']:.4g}`。",
        f"- estimated surface velocity：`{result['estimated_surface_velocity_mps']:.4g}` m/s。",
        f"- expected sanity range：`{result['expected_rayleigh_like_range_mps']}` m/s。",
        f"- rayleigh_like_event_detected：`{result['rayleigh_like_event_detected']}`。",
        f"- estimation method：`{result['velocity_estimation_method']}`。",
        f"- source type：`{result.get('source_type')}`。",
        f"- source depth：`{result.get('source_depth_m')}` m。",
        f"- pick velocity window：`{result.get('pick_vmin_mps')}` - `{result.get('pick_vmax_mps')}` m/s。",
        f"- rayleigh_pick_interpretation：{result.get('rayleigh_pick_interpretation')}",
        "",
        "## 边界",
        "",
        "- 顶部自由表面为近似 traction-free 处理。",
        "- 当前格式是 collocated-grid minimal prototype，精度和稳定性不等同于 staggered-grid/PML 工业实现。",
        "- 该结果只能说明出现 Rayleigh-like surface event 的 sanity check，不能作为工程级 Rayleigh 正演。",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_elastic2d_void_scattering_report(path: Path, result: dict[str, Any]) -> None:
    """写出 elastic2d void-like scattering 报告。"""

    lines = [
        "# elastic2d void / low Vs scattering 报告",
        "",
        "本报告比较背景模型和低 Vp/低 Vs/低密度 void-like 扰动模型的 surface gather。",
        "",
        f"- residual_energy：`{result['residual_energy']:.4g}`。",
        f"- relative_residual_energy：`{result['relative_residual_energy']:.4g}`。",
        f"- void_residual_visible：`{result['void_residual_visible']}`。",
        f"- scatter center：x=`{result['scatter_x_m']:.4g}` m, z=`{result['scatter_z_m']:.4g}` m。",
        f"- parameter sensitivity best case：`{result.get('parameter_sensitivity', {}).get('best_case')}`。",
        f"- parameter sensitivity best residual energy：`{result.get('parameter_sensitivity', {}).get('best_residual_energy')}`。",
        "",
        "## 解释",
        "",
        "- 低速扰动可产生可见 residual，但它不是严格空腔边界条件。",
        "- residual envelope 会与局部 kinematic diffraction curve 做叠加，检查运动学走时在哪些位置仍有解释力。",
        "- elastic2d 会出现振幅、频率、尾波和多路径等运动学模型没有的效应。",
        "- 下一步需要更严格 free surface、PML 和 staggered-grid 精度硬化。",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_elastic2d_das_response_report(path: Path, result: dict[str, Any]) -> None:
    """写出 elastic2d DAS-like gauge response 报告。"""

    lines = [
        "# elastic2d DAS-like gauge response 报告",
        "",
        "本报告从 elastic2d surface velocity 近似派生 point receiver 和 gauge-length strain 响应。",
        "",
        "- point_receiver_gather 使用 surface vz。",
        "- gauge_length_strain_gather 使用 surface vx 沿 x 方向的 gauge-length finite difference。",
        "- gauge length 会改变局部散射响应，短波长事件可能被增强或削弱。",
        "- point receiver 和 DAS-like strain 不能混为一谈。",
        "- 后续三维 receiver polyline 应沿局部切向方向计算 strain。",
        "",
        f"- point shape：`{result['point_shape']}`。",
        f"- strain shape：`{result['strain_shape']}`。",
        f"- strain_rms / point_rms：`{result['strain_to_point_rms_ratio']:.4g}`。",
        f"- best_source_type_for_gauge：`{result.get('best_source_type_for_gauge')}`。",
        f"- best_gauge_length_m：`{result.get('best_gauge_length_m')}`。",
        f"- gauge_void_residual_rms：`{result.get('gauge_void_residual_rms')}`。",
        "- das_gauge_final_status：`nonzero_but_weak_not_for_default_localization`。",
        "- default localization：`False`，当前不能默认使用 gauge strain。",
        "",
        "## Stage 5H 统一解释",
        "",
        "- 旧相对指标可能显示 0：strain_rms / point_rms 会被强 point receiver 分量和极小 gauge 有限差分同时压低。",
        "- 绝对弱响应检查能显示非零：Stage 5H 直接检查 velocity gauge strain RMS，并使用非零 receiver pair。",
        "- 非零不代表有效：当前仍未校准光纤切向方向、gauge length、仪器响应和真实接收道距。",
    ]
    nonzero = result.get("nonzero_check") or {}
    if nonzero:
        lines.extend(
            [
                "",
                "## Stage 5E 非零响应检查",
                "",
                f"- das_gauge_nonzero_status：`{nonzero.get('das_gauge_nonzero_status')}`。",
                f"- best_velocity_gauge_case：`{nonzero.get('best_velocity_gauge_case')}`。",
                f"- best_velocity_gauge_rms：`{nonzero.get('best_velocity_gauge_rms')}`。",
                f"- best_velocity_gauge_source_type：`{nonzero.get('best_velocity_gauge_source_type')}`。",
                f"- best_velocity_gauge_length_m：`{nonzero.get('best_velocity_gauge_length_m')}`。",
                f"- best_displacement_gauge_case：`{nonzero.get('best_displacement_gauge_case')}`。",
                f"- best_displacement_gauge_rms：`{nonzero.get('best_displacement_gauge_rms')}`。",
                f"- default_localization_should_use_gauge_strain：`{nonzero.get('default_localization_should_use_gauge_strain')}`。",
                f"- diagnosis：{nonzero.get('diagnosis')}",
                f"- old_relative_metric_zero_reason：{nonzero.get('old_relative_metric_zero_reason')}",
                f"- absolute_nonzero_reason：{nonzero.get('absolute_nonzero_reason')}",
                f"- required_for_real_das：`{nonzero.get('required_for_real_das')}`",
                "",
                "若 gauge strain 为零或很弱，必须明确禁止默认纳入定位；即使非零，也仍需真实 DAS gauge/方向/仪器响应校准。",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_elastic_vs_kinematic_report(path: Path, result: dict[str, Any]) -> None:
    """写出 elastic2d 与 kinematic 对照报告。"""

    lines = [
        "# elastic2d 与 layered_kinematic 对照报告",
        "",
        "本报告把 elastic2d residual gather 与局部 kinematic diffraction curve 叠加，检查运动学走时对 elastic residual 的解释能力。",
        "",
        f"- curve_energy_ratio：`{result['curve_energy_ratio']:.4g}`。",
        f"- residual_energy_near_kinematic_curve_ratio：`{result.get('residual_energy_near_kinematic_curve_ratio')}`。",
        f"- residual_energy_off_curve_ratio：`{result.get('residual_energy_off_curve_ratio')}`。",
        f"- best_time_shift_ms：`{result.get('best_time_shift_ms')}`。",
        f"- kinematic_curve_explained_fraction：`{result.get('kinematic_curve_explained_fraction')}`。",
        f"- elastic_extra_event_fraction：`{result.get('elastic_extra_event_fraction')}`。",
        f"- main conclusion：{result['main_conclusion']}",
        "",
        "## 结论边界",
        "",
        "- layered_kinematic 曲线可解释部分主要到时，但不能解释完整振幅、频率、尾波和多路径。",
        "- 低解释比例可能来自 Rayleigh-like 拾取未通过、body wave / boundary reflection 占主导，或 collocated-grid/free-surface 原型仍不稳定。",
        "- 这说明当前 kinematic localization 不能直接用 elastic residual 的全波形能量来评价迁移能力。",
        "- matched wavelet、frequency shift、semblance 等定位属性暂不应基于该 elastic residual 强行调参。",
        "- x-y-h 三维定位仍可继续使用 kinematic 主线做快速候选区扫描。",
        "- 深度、横向 y、振幅和频率解释必须等 elastic validation 更成熟后再推进。",
        "- 当前结果是科研候选区，不是工程确诊。",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_velocity_model_visualization_report(path: Path, result: dict[str, Any]) -> None:
    """写出当前速度模型可视化报告。"""

    diff = result["uniform_vs_active_travel_time_difference"]
    sampling = result["sampling_path"]
    lines = [
        "# 当前速度模型可视化报告",
        "",
        "本报告回答当前主流程到底是不是 layered / heterogeneous velocity，而不是只存在源码文件。",
        "",
        f"- active velocity_model_type：`{result['active_velocity_model_type']}`",
        f"- layer depths m：`{result['layer_depths_m']}`",
        f"- layer velocities m/s：`{result['layer_rayleigh_velocities_mps']}`",
        f"- sampling path velocity min/max/mean：`{sampling['velocity_min_mps']}` / `{sampling['velocity_max_mps']}` / `{sampling['velocity_mean_mps']}` m/s",
        f"- uniform vs active direct RMS difference：`{diff['direct_diff_rms_ms']:.4g}` ms",
        f"- uniform vs active direct max abs difference：`{diff['direct_diff_max_abs_ms']:.4g}` ms",
        "",
        "## 解释",
        "",
        "- 当前 layered_kinematic 使用等效 Rayleigh 速度模型和 straight-ray 路径采样积分。",
        "- 该模型不是完整 Vp/Vs/rho 弹性模型，也不是速度反演结果。",
        "- elastic2d_prototype 的 Vp/Vs/rho 是独立 validation 参数，与本报告中的 Rayleigh equivalent velocity 不属于同一层级。",
        "- 下一步若要进入真实数据，应优先做实测速度标定或速度反演约束。",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
