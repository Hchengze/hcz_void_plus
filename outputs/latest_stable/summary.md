# latest_stable Stage 5G 摘要

## 当前阶段

- stage = Stage 5G
- commit id：`128d807`
- 任务名称：`Stage 5G latest_stable 三类结果重构 + 图件中文化 + 动图整合 + 三维可视化增强`
- 运行时间：`2026-07-05T01:54:17`
- active_velocity_model = `layered`
- active_forward_engine = `layered_kinematic`
- validation_forward = `elastic2d/staggered`
- ready_for_2p5d = `False`

## 三类精选结果

- forward 图件数：`10`
- localization 图件数：`6`
- error_analysis 图件数：`7`
- 静态图总数：`23`
- 动图总数：`2`
- 报告总数：`12`

## 三维定位结论

- recommended/best location：x=`60.0` m, y=`10.0` m, depth=`2.5` m
- truth_error：`1.118033988749895` m
- 3D high-score span：x=`0.0` m, y=`4.0` m, depth=`0.0` m
- high-score point count：`3`

## Rayleigh 与 DAS 状态

- best_rayleigh_benchmark_case：`staggered_traction_variant`
- rayleigh_like_event_detected：`False`
- rayleigh_velocity_relative_error：`0.2028480598664669`
- das_gauge_final_status：`nonzero_but_weak_not_for_default_localization`
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
- figures/error_analysis/fig_stage5g_status_badge.png

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

- copied：`43`
- missing：`0`
