# latest_stable Stage 5I 摘要

## 当前阶段

- stage = Stage 5I
- previous_stage = Stage 5H
- algorithm_commit = `f22cc22`
- latest_stable_commit = `8fae3a9`
- previous_latest_stable_commit = `a202fee`
- source_run_dir = `outputs\stage5i_run_20260705_132534`
- generated_time = `2026-07-05T13:27:40`
- 任务名称：`Stage 5I 三维运动学正演-定位一致性修复 + 三维多属性反演增强`
- active_velocity_model = `layered`
- active_forward_engine = `layered_kinematic`
- validation_forward = `elastic2d/staggered`
- ready_for_2p5d = `False`

## Stage 5I 三维反演主线

- scan_candidate_uses_path_integration = `True`
- scan_uses_representative_velocity = `False`
- multi_attribute_inversion_enabled = `True`
- posterior_volume_status = `generated`
- posterior_peak_location = `{'x_m': 52.0, 'y_m': 12.0, 'depth_m': 2.5}`
- posterior_mean_location = `{'x_m': 65.32635052587617, 'y_m': 10.068445559182855, 'depth_m': 3.9003988407759906}`
- posterior_uncertainty_axes = `[26.986846401825968, 5.142243049077285, 1.706998715345629]`
- geometry_resolution_status = `computed`
- ambiguity_warning = `True`

## 三类精选结果

- forward 图件数：`10`
- localization 图件数：`7`
- error_analysis 图件数：`7`
- 静态图总数：`24`
- 动图总数：`2`
- 报告总数：`10`
- latest_stable_tree_snapshot_status：`pass`
- manual_review_readiness_status：`pass`

## 三维定位结论

- recommended/best location：x=`60.0` m, y=`6.0` m, depth=`2.5` m
- truth_error：`3.0413812651491097` m
- 3D high-score span：x=`8.0` m, y=`12.0` m, depth=`1.0` m
- high-score point count：`20`

## Rayleigh 与 DAS 状态

- best_rayleigh_benchmark_case：`staggered_traction_variant`
- rayleigh_like_event_detected：`False`
- rayleigh_velocity_relative_error：`0.2028480598664669`
- picked_event_interpretation：`likely_boundary_reflection_or_late_surface_coda`
- likely_surface_wave_score：`0.18860776053413242`
- likely_boundary_reflection_score：`0.25`
- likely_body_wave_score：`0.2`
- late_coda_score：`0.2`
- failure_reason_ranked：`['boundary_reflection', 'body_wave_or_direct_leakage', 'late_coda_or_grid_dispersion', 'surface_wave_candidate']`
- das_gauge_final_status：`nonzero_but_weak_not_for_default_localization`
- das_best_velocity_gauge_rms：`5.40751067390065e-09`
- DAS gauge 默认定位使用：`False`

## 图件质量与中文化

- figure_quality_check_status：`pass`
- empty_figure_count：`0`
- figure_deduplication_status：`pass`
- duplicate_figure_count：`0`
- figure_language_check_status：`pass`
- english_figure_count：`0`
- figure_label_audit_status：`pass`
- english_case_label_count：`0`

## 人工复查准备度

- manual_review_figure_count：`10`
- manual_review_animation_count：`2`
- required_3d_figures_present：`True`
- required_animations_present：`True`

## manual_review_figures

- figures/forward/fig_geometry_3d_overview.png
- figures/forward/fig_velocity_model_active_badge.png
- figures/forward/fig_velocity_model_physics_bridge.png
- figures/forward/fig_elastic2d_rayleigh_benchmark_matrix.png
- figures/forward/fig_elastic2d_rayleigh_velocity_error.png
- figures/forward/fig_elastic2d_das_best_case.png
- figures/localization/fig_3d_high_score_region.png
- figures/localization/fig_recommended_location_3d.png
- figures/localization/fig_3d_uncertainty_box.png
- figures/error_analysis/fig_stage5i_status_badge.png

## manual_review_animations

- animations/forward/anim_multishot_forward_overview.gif
- animations/forward/anim_single_shot_wavefield.gif

## 当前限制

- `layered_kinematic` 仍是当前主定位 forward，属于 straight-ray kinematic approximation。
- `elastic2d/staggered` 仍是 validation forward，不是工业级模拟。
- Rayleigh benchmark 未通过前，`ready_for_2p5d` 必须为 False。
- DAS-like gauge strain 非零但弱且未校准，不默认用于定位，也不等同真实 DAS 仪器响应。
- 2D elastic 只服务三维道路 DAS-like 场景的局部物理验证，不能替代 `source_xyz / receiver_xyz / candidate_xyz` 和 x-y-depth 三维定位。

## 导出记录

- copied：`45`
- missing：`0`
