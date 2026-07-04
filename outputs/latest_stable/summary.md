# latest_stable 稳定成果摘要

## 本轮信息

- commit id：`e88e5c1`
- 任务名称：`Stage 5D elastic2d 加固 + 速度模型主线核验 + 图件自检`
- 运行时间：`2026-07-04T19:12:23`
- 来源目录：`outputs\stage5d_run_20260704_191133`

## 当前近似条件

- `kinematic approximation`
- `DAS-like response approximation`
- active forward engine：`layered_kinematic`
- available forward engines：`['kinematic_baseline', 'layered_kinematic', 'acoustic2d_prototype', 'elastic2d_prototype']`
- forward modeling stage：`F1 layered_kinematic active, F2 acoustic2d validation, F3 elastic2d_prototype validation`
- `kinematic_surface_response`，不是真实弹性波场模拟
- Rayleigh 深度权重是 `exp(-h / penetration_depth)` 简化近似，不是严格模态深度核

## 最佳定位结果

- best_location：x=`60.0` m，y=`10.0` m，h=`2.5` m
- truth_error：`1.118033988749895` m

## unweighted 与 weighted best 对比

- unweighted_best：x=`60.0` m，y=`10.0` m，h=`2.5` m
- weighted_best：x=`60.0` m，y=`10.0` m，h=`2.5` m
- unweighted -> weighted 差异：dx=`0.0` m，dy=`0.0` m，dh=`0.0` m，三维距离=`0.0` m

## 推荐位置与不确定性

- recommended_location_type：`uncertainty_interval`
- recommended_location：`{'x_m': 60.0, 'y_m': 10.0, 'depth_m': 2.5, 'x_interval_m': [60.0, 60.0], 'y_interval_m': [8.0, 12.0], 'depth_interval_m': [2.5, 2.5], 'component_boxes': [{'point_count': 3, 'x_min_m': 60.0, 'x_max_m': 60.0, 'y_min_m': 8.0, 'y_max_m': 12.0, 'depth_min_m': 2.5, 'depth_max_m': 2.5, 'x_span_m': 0.0, 'y_span_m': 4.0, 'depth_span_m': 0.0}]}`
- recommended_reason：weighted_best 受到深度权重影响，或触发边界、宽 y、unweighted-weighted 分歧等 warning；因此不把 weighted_best 作为单点推荐，而采用 unweighted_best 作为参考点，并以三维高分区区间表达不确定性。
- depth uncertainty interval：`[2.5, 2.5]` m
- 3D high-score span：x=`0.0` m，y=`4.0` m，depth=`0.0` m
- high-score point count：`3`

## score method 对比

- comparison methods：`['diffraction_energy_stack', 'normalized_energy_stack']`
- depth stability reference：`{'best_unweighted_depth_method': 'diffraction_energy_stack', 'best_unweighted_depth_abs_error_m': 0.5, 'note': '仅比较当前场景下 unweighted_best 的深度误差，不代表通用优劣。'}`

## depth prior sensitivity

- factors：`['0.5', '1.0', '2.0', 'off']`

## Stage 4B 算法有效性验证

- preprocessing best truth-error case：`none`
- preprocessing narrowest y-depth case：`bandpass_trace_normalization_taper_direct_mute`
- FK direct wave reduction ratio：`0.0316551481300289`
- FK diffraction preservation ratio：`0.9796773553296154`
- multi_attribute improved over energy：`False`
- multi_attribute best group：`energy_only`
- geometry best y-resolution case：`geometry_case_A_single_side_line`
- geometry best depth-stability case：`geometry_case_A_single_side_line`
- geometry best truth-error case：`geometry_case_A_single_side_line`
- high-score component count：`1`
- multi-region warning：`False`

## Stage 5A 稳定算法与速度模型升级

- stable code area：`code/current_3d_algorithm/`
- default velocity model：`layered`
- velocity ablation best truth-error case：`uniform`
- velocity ablation best depth case：`uniform`
- largest travel-time residual case：`layered_with_anomaly_perturbation`
- model mismatch safest case：`uniform_forward_uniform_scan`
- model mismatch riskiest case：`layered_forward_uniform_scan`
- minimum recommended velocity model：`layered`
- note：分层/非均匀速度仍是 straight-ray kinematic approximation，不是 3D elastic wavefield。

## Stage 5B/5C/5D 正演技术路线与 elastic2d 验证

- latest_stable_curated：`True`
- forward_engine_active：`layered_kinematic`
- forward_engine_available：`['kinematic_baseline', 'layered_kinematic', 'acoustic2d_prototype', 'elastic2d_prototype']`
- forward_engine_next_required：`elastic2d accuracy/stability hardening + 2.5D multi-section validation`
- forward_modeling_stage：`F1 layered_kinematic active, F2 acoustic2d validation, F3 elastic2d_prototype validation`
- validation_forward_available：`['acoustic2d_prototype', 'elastic2d_prototype']`
- layered_vs_baseline travel-time RMS residual：`57.07585810059442` ms
- layered_vs_baseline synthetic relative difference：`1.320055775620881`
- acoustic2d_prototype_status：CFL stable=`True`，snapshot_count=`6`
- elastic2d_prototype_status：`minimal_velocity_stress_validation`
- rayleigh_validation_status：`False`
- void_scattering_validation_status：`True`
- das_gauge_response_status：`component_and_gauge_length_checked`
- elastic_vs_kinematic_main_conclusion：layered/局部 kinematic 曲线只能解释 elastic residual 的一部分能量；曲线外 residual 代表振幅、尾波、多路径、边界和弹性模式等运动学模型没有的效应。
- elastic2d_design_status：`minimal_prototype_available_validation_only`
- note：`acoustic2d_prototype` 是 acoustic wave-equation infrastructure validation，不能代表 Rayleigh/free-surface/void scattering；`elastic2d_prototype` 是最小科研验证原型，仍不替代主定位 forward。

## Stage 5D 速度模型核验、图件自检与 elastic2d 加固

- repository_health_status：`pass`
- figure_self_check_status：`pass`
- figure_self_check passed/failed：`37` / `0`
- active_velocity_model_type：`layered`
- active_velocity_model_confirmed：`True`
- velocity_model_used_by_direct：`True`
- velocity_model_used_by_scatter：`True`
- velocity_model_used_by_scan：`True`
- velocity_model_visualization_status：`generated`
- uniform_vs_layered_direct_rms_ms：`215.69599998465384`
- rayleigh_like_event_detected：`False`
- rayleigh_pick_interpretation：拾取速度偏慢，可能受边界反射、sponge 衰减或弱表面事件影响。
- void_residual_energy_best_case：`vertical_force_r1.5_vs0.2` / `1.1075624099111773e-16`
- das_gauge_response_best_case：source=`vertical_force`，gauge_length=`0.5` m
- elastic_vs_kinematic_explained_fraction：`0.00022196748680872161`

## 基础置信度指标

- peak sharpness：`2.0599457066651934`
- score contrast：`8.187699231656023`
- score percentile：`100.0`
- multi-shot consistency CV：`0.12786256485343217`
- y-depth coupling warning：`False`
- best depth boundary warning：`False`
- wide y high-score zone warning：`True`
- raw/weighted divergence warning：`False`
- shallow bias warning：`False`
- low confidence flag：`medium-low`

## 推荐人工重点查看

- figures/core/fig_geometry_layout_check.png
- figures/core/fig_shot_gather_000.png
- figures/core/fig_best_location_map.png
- figures/core/fig_confidence_diagnostics.png
- figures/core/fig_forward_roadmap_status.png
- figures/forward/fig_forward_engine_comparison.png
- figures/forward/fig_layered_kinematic_vs_baseline_gather.png
- figures/forward/fig_acoustic2d_wavefield_snapshots.png
- figures/forward/fig_acoustic2d_shot_gather.png
- figures/forward/fig_elastic2d_rayleigh_wavefield_snapshots.png
- figures/forward/fig_elastic2d_surface_gather.png
- figures/forward/fig_elastic2d_rayleigh_velocity_check.png
- figures/forward/fig_elastic2d_rayleigh_pick_diagnostics.png
- figures/forward/fig_elastic2d_void_scattering_residual.png
- figures/forward/fig_elastic2d_void_diffraction_overlay.png
- figures/forward/fig_elastic2d_void_parameter_sensitivity.png
- figures/forward/fig_elastic2d_void_residual_energy_map.png
- figures/forward/fig_elastic2d_das_gauge_response.png
- figures/forward/fig_elastic2d_das_component_comparison.png
- figures/forward/fig_elastic2d_das_gauge_length_sensitivity.png
- figures/forward/fig_elastic_vs_kinematic_overlay.png
- figures/forward/fig_elastic_vs_kinematic_residual_energy.png
- figures/forward/fig_elastic_vs_kinematic_energy_partition.png
- figures/localization/fig_scan_x_depth_slice.png
- figures/localization/fig_scan_x_y_slice.png
- figures/localization/fig_multi_attribute_ablation.png
- figures/uncertainty/fig_3d_high_score_components.png
- figures/uncertainty/fig_x_y_depth_uncertainty_slices.png
- figures/uncertainty/fig_recommendation_decision_flow.png
- figures/diagnostics/fig_velocity_model_comparison.png
- figures/diagnostics/fig_model_mismatch_error_summary.png
- figures/diagnostics/fig_depth_prior_sensitivity.png
- figures/diagnostics/fig_velocity_model_profile_current.png
- figures/diagnostics/fig_velocity_model_2d_slice_current.png
- figures/diagnostics/fig_velocity_sampling_paths_current.png
- figures/diagnostics/fig_uniform_vs_layered_travel_time_difference.png
- figures/diagnostics/fig_velocity_model_active_badge.png
- figures/diagnostics/anim_pseudo_wavefield.gif
- reports/core/report_full_pipeline.md
- reports/core/report_confidence.md
- reports/core/report_figure_self_check.md
- reports/forward/report_forward_engine_ablation.md
- reports/forward/report_acoustic2d_prototype.md
- reports/forward/report_elastic2d_rayleigh_validation.md
- reports/forward/report_elastic2d_void_scattering.md
- reports/forward/report_elastic2d_das_response.md
- reports/forward/report_elastic_vs_kinematic.md
- reports/localization/report_multi_attribute_ablation.md
- reports/localization/report_geometry_ablation.md
- reports/diagnostics/report_velocity_model_ablation.md
- reports/diagnostics/report_model_mismatch.md
- reports/diagnostics/report_velocity_model_audit.md
- reports/diagnostics/report_velocity_model_visualization.md
- reports/core/report_repository_health.md

## 导出记录

- 已复制精选文件数量：`60`
- 缺失精选文件数量：`1`

## 当前限制

本目录只保存本轮最新、最值得人工检查的精选结果。时间戳运行目录保留完整本地结果，但大型数组、快照和中间产物默认不纳入 Git。当前定位和置信度仍是科研算法原型诊断，不能作为工程确诊结论。
