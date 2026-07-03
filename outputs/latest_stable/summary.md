# latest_stable 稳定成果摘要

## 本轮信息

- commit id：`8c1bed3`
- 任务名称：`Stage 4A Reference 审计接入 + 三维观测几何泛化 + 预处理与定位算法增强`
- 运行时间：`2026-07-03T15:55:25`
- 来源目录：`outputs\stage4a_run_20260703_155513`

## 当前近似条件

- `kinematic approximation`
- `DAS-like response approximation`
- `kinematic_surface_response`，不是真实弹性波场模拟
- Rayleigh 深度权重是 `exp(-h / penetration_depth)` 简化近似，不是严格模态深度核

## 最佳定位结果

- best_location：x=`60.0` m，y=`9.0` m，h=`2.5` m
- truth_error：`0.5` m

## unweighted 与 weighted best 对比

- unweighted_best：x=`60.0` m，y=`9.0` m，h=`2.5` m
- weighted_best：x=`60.0` m，y=`9.0` m，h=`0.5` m
- unweighted -> weighted 差异：dx=`0.0` m，dy=`0.0` m，dh=`-2.0` m，三维距离=`2.0` m

## 推荐位置与不确定性

- recommended_location_type：`uncertainty_interval`
- recommended_location：`{'x_m': 60.0, 'y_m': 9.0, 'depth_m': 2.5, 'x_interval_m': [60.0, 60.0], 'y_interval_m': [6.0, 13.0], 'depth_interval_m': [0.5, 6.0]}`
- recommended_reason：weighted_best 受到深度权重影响且触发边界/宽 y/unweighted-weighted 分歧等 warning；因此不把 weighted_best 作为单点推荐，而采用 unweighted_best 作为参考点，并以三维高分区区间表达不确定性。
- depth uncertainty interval：`[0.5, 6.0]` m
- 3D high-score span：x=`0.0` m，y=`7.0` m，depth=`5.5` m
- high-score point count：`87`

## score method 对比

- comparison methods：`['diffraction_energy_stack', 'normalized_energy_stack']`
- depth stability reference：`{'best_unweighted_depth_method': 'diffraction_energy_stack', 'best_unweighted_depth_abs_error_m': 0.5, 'note': '仅比较当前场景下 unweighted_best 的深度误差，不代表通用优劣。'}`

## depth prior sensitivity

- factors：`['0.5', '1.0', '2.0', 'off']`

## 基础置信度指标

- peak sharpness：`1.1147675967113735`
- score contrast：`5.447588478737515`
- score percentile：`100.0`
- multi-shot consistency CV：`0.27957500409397734`
- y-depth coupling warning：`True`
- best depth boundary warning：`False`
- wide y high-score zone warning：`True`
- raw/weighted divergence warning：`True`
- shallow bias warning：`True`
- low confidence flag：`low`

## 推荐人工重点查看

- figures/fig_geometry_layout_check.png
- figures/fig_source_anomaly_receiver_path_section.png
- figures/fig_rayleigh_depth_sensitivity.png
- figures/fig_shot_gather_000.png
- figures/fig_diffraction_travel_time_curves.png
- figures/fig_scan_x_depth_slice.png
- figures/fig_scan_x_y_slice.png
- figures/fig_best_location_map.png
- figures/fig_raw_vs_weighted_best_location.png
- figures/fig_raw_vs_weighted_x_depth_slice.png
- figures/fig_y_high_score_width_check.png
- figures/fig_confidence_diagnostics.png
- figures/fig_score_method_depth_comparison.png
- figures/fig_3d_high_score_uncertainty_summary.png
- figures/fig_x_y_depth_uncertainty_slices.png
- figures/fig_3d_geometry_overview.png
- figures/fig_receiver_source_3d_layout.png
- figures/fig_anomaly_3d_scatter_points.png
- figures/fig_multi_attribute_score_comparison.png
- figures/fig_depth_prior_sensitivity.png
- figures/fig_preprocessing_comparison.png
- animations/anim_pseudo_wavefield.gif
- reports/report_full_pipeline.md
- reports/report_confidence.md
- reports/report_score_method_comparison.md
- reports/report_depth_prior_sensitivity.md

## 导出记录

- 已复制精选文件数量：`28`
- 缺失精选文件数量：`0`

## 当前限制

本目录只保存本轮最新、最值得人工检查的精选结果。时间戳运行目录保留完整本地结果，但大型数组、快照和中间产物默认不纳入 Git。当前定位和置信度仍是科研算法原型诊断，不能作为工程确诊结论。
