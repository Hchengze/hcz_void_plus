# Reference-backed 算法吸收矩阵

本矩阵用于把 reference、旧代码和文献算法点转化为可审计的项目实现。当前项目不直接复制无许可证第三方代码；所有进入 `src/` 的算法均为本项目重写的科研原型实现。

| reference item | 文献或旧代码中的算法点 | 物理目的 | 本项目实现函数 | 对应测试 | 对应输出图 | 是否改善结果 | 当前限制 |
|---|---|---|---|---|---|---|---|
| Rayleigh-wave diffraction 处理思路 | 直达面波压制 | 削弱强直达面波，暴露弱绕射事件 | `src.features.direct_wave_mute.mute_direct_wave` | `tests/test_features.py`, `tests/test_preprocessing_ablation.py` | `fig_preprocessing_ablation_summary.png`, `fig_diffraction_travel_time_curves.png` | 已进入默认流程，效果由消融报告给出 | 仍是预测走时窗 taper/subtract，不是自适应面波分离 |
| Rayleigh-wave FK / f-v filtering 思路 | FK / f-v 速度扇区滤波 | 在 time-channel 域压制不合速度范围的能量 | `src.preprocessing.fk_filter.fk_velocity_filter` | `tests/test_fk_filter_validation.py` | `fig_fk_spectrum_before_after.png`, `fig_fk_filter_effect_on_gather.png` | 接口已建立，是否增强绕射由 Stage 4B 验证报告判断 | 仅适用于近似直线、等间距 receiver；polyline 仅作近似 QC |
| Diffraction travel-time curve fitting | 绕射走时曲线匹配 | 检查理论散射曲线是否对应炮集能量事件 | `src.localization.travel_time.compute_candidate_diffraction_times`, `src.visualization.plot_physical_diagnostics.plot_diffraction_travel_time_curves` | `tests/test_scan.py`, `tests/test_geometry.py` | `fig_diffraction_travel_time_curves.png` | 已用于 QC，不直接等价为成像结果 | 运动学走时，不含弹性波型转换和复杂速度结构 |
| Ricker wavelet matching | matched wavelet score | 判断候选曲线附近局部波形是否像震源子波 | `src.localization.attribute_scoring.compute_matched_wavelet_score` | `tests/test_matched_wavelet_score.py` | `fig_matched_wavelet_score_comparison.png` | Stage 4B 消融比较其是否优于 energy | 使用简化 Ricker 模板，真实数据需估计源子波 |
| Multi-shot coherence / semblance | semblance / 多炮一致性 | 检查沿候选绕射曲线对齐后波形是否一致 | `src.localization.attribute_scoring.compute_semblance_score` | `tests/test_semblance_score.py` | `fig_semblance_score_volume_slice.png` | Stage 4B 消融验证是否减少假高分 | 仍是局部窗口 semblance，不是完整成像条件 |
| Attenuation / spectral attribute | frequency shift / 高频衰减属性 | 诊断异常附近是否存在谱质心下降 | `src.localization.attribute_scoring.compute_frequency_shift_score` | `tests/test_frequency_shift_attribute.py` | `fig_frequency_shift_attribute.png` | 已从 0 占位升级为最小可用诊断，默认权重为 0 | 不是 Q 反演，不应单独解释为空洞证据 |
| 3D acquisition geometry | 三维 source-receiver-candidate 几何 | 避免把问题退化为二维 x-depth 剖面 | `src.geometry.receiver_polyline.build_receiver_xyz`, `src.geometry.source_layout.build_source_xyz`, `src.localization.travel_time.compute_candidate_diffraction_times` | `tests/test_receiver_polyline.py`, `tests/test_source_layout.py`, `tests/test_geometry_ablation.py` | `fig_3d_geometry_overview.png`, `fig_geometry_ablation_best_locations.png` | Stage 4B 几何消融评估非共线/双侧震源是否改善 y-depth | 当前仍是 3D kinematic geometry，不是 3D elastic wavefield |
| 3D uncertainty expression | 三维高分区不确定性表达 | 用候选体和连通域替代单点确诊 | `src.confidence.uncertainty_region.compute_3d_high_score_region`, `src.localization.connected_components.label_high_score_components` | `tests/test_3d_connected_components.py`, `tests/test_confidence.py` | `fig_3d_high_score_components.png`, `fig_recommendation_decision_flow.png` | 已能触发 multi_region_warning 并影响 recommended_location_type | 不是概率置信区间，也不是工程风险边界 |

## 当前结论

Stage 4B 的目标不是证明所有参考算法都已经有效，而是把每个算法点变成可运行、可测试、可出图、可报告的闭环。若某个算法点在当前默认三维场景中没有改善结果，报告必须诚实记录“接口已建立，效果待验证”。
# Stage 5A 增补：速度模型算法矩阵

| reference item | 算法点 | 物理目的 | 本项目实现函数 | 对应测试 | 对应输出图 | 是否改善结果 | 当前限制 |
|---|---|---|---|---|---|---|---|
| 近地表分层介质常识 | layered effective Rayleigh velocity | 表达路面、基层、土体层速度差异 | `src.model.layered_velocity.LayeredVelocityModel` | `tests/test_layered_velocity_model.py` | `fig_layered_velocity_profile.png` | Stage 5A 起纳入验证 | straight-ray，不做射线弯曲 |
| 横向非均匀道路介质 | lateral velocity gradient | 表达回填和沿线速度缓变 | `src.model.heterogeneous_velocity.LateralGradientVelocityModel` | `tests/test_heterogeneous_velocity_model.py` | `fig_velocity_model_comparison.png` | 用于风险诊断 | 线性梯度近似 |
| 局部低速扰动 | localized low velocity zone | 检查低速带是否诱发定位偏移 | `LocalizedLowVelocityZoneModel` | `tests/test_heterogeneous_velocity_model.py` | `fig_model_mismatch_error_summary.png` | 用于错配风险诊断 | 不产生真实散射，只改走时 |
| 模型错配 | forward/scan velocity mismatch | 评估真实介质与反演假设不一致的风险 | `src.validation.model_mismatch.run_model_mismatch_experiment` | `tests/test_model_mismatch.py` | `fig_model_mismatch_error_summary.png` | Stage 5A 新增 | 小规模轻量实验 |

