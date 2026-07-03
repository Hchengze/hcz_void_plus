# latest_stable 稳定成果摘要

## 本轮信息

- commit id：`c08fab8`
- 任务名称：`Stage 4B Reference-backed 算法有效性验证 + 三维几何破局 + 代码可审计性修复`
- 运行时间：`2026-07-03T19:32:42`
- 来源目录：`outputs\stage4b_run_20260703_193225`

## 当前近似条件

- `kinematic approximation`
- `DAS-like response approximation`
- `kinematic_surface_response`，不是真实弹性波场模拟
- Rayleigh 深度权重是 `exp(-h / penetration_depth)` 简化近似，不是严格模态深度核

## 最佳定位结果

- best_location：x=`60.0` m，y=`10.0` m，h=`2.5` m
- truth_error：`1.118033988749895` m

## unweighted 与 weighted best 对比

- unweighted_best：x=`60.0` m，y=`10.0` m，h=`2.5` m
- weighted_best：x=`60.0` m，y=`10.0` m，h=`0.5` m
- unweighted -> weighted 差异：dx=`0.0` m，dy=`0.0` m，dh=`-2.0` m，三维距离=`2.0` m

## 推荐位置与不确定性

- recommended_location_type：`uncertainty_interval`
- recommended_location：`{'x_m': 60.0, 'y_m': 10.0, 'depth_m': 2.5, 'x_interval_m': [60.0, 60.0], 'y_interval_m': [6.0, 14.0], 'depth_interval_m': [0.5, 5.5], 'component_boxes': [{'point_count': 24, 'x_min_m': 60.0, 'x_max_m': 60.0, 'y_min_m': 6.0, 'y_max_m': 14.0, 'depth_min_m': 0.5, 'depth_max_m': 5.5, 'x_span_m': 0.0, 'y_span_m': 8.0, 'depth_span_m': 5.0}]}`
- recommended_reason：weighted_best 受到深度权重影响，或触发边界、宽 y、unweighted-weighted 分歧等 warning；因此不把 weighted_best 作为单点推荐，而采用 unweighted_best 作为参考点，并以三维高分区区间表达不确定性。
- depth uncertainty interval：`[0.5, 5.5]` m
- 3D high-score span：x=`0.0` m，y=`8.0` m，depth=`5.0` m
- high-score point count：`24`

## score method 对比

- comparison methods：`['diffraction_energy_stack', 'normalized_energy_stack']`
- depth stability reference：`{'best_unweighted_depth_method': 'diffraction_energy_stack', 'best_unweighted_depth_abs_error_m': 0.5, 'note': '仅比较当前场景下 unweighted_best 的深度误差，不代表通用优劣。'}`

## depth prior sensitivity

- factors：`['0.5', '1.0', '2.0', 'off']`

## Stage 4B 算法有效性验证

- preprocessing best truth-error case：`bandpass_trace_normalization_taper_direct_mute`
- preprocessing narrowest y-depth case：`bandpass_trace_normalization_taper_direct_mute`
- FK direct wave reduction ratio：`0.0673824082550083`
- FK diffraction preservation ratio：`1.008050635677625`
- multi_attribute improved over energy：`False`
- multi_attribute best group：`energy_only`
- geometry best y-resolution case：`geometry_case_C_two_side_sources`
- geometry best depth-stability case：`geometry_case_A_single_side_line`
- geometry best truth-error case：`geometry_case_A_single_side_line`
- high-score component count：`1`
- multi-region warning：`False`

## 基础置信度指标

- peak sharpness：`1.4339687136174144`
- score contrast：`5.424023491123463`
- score percentile：`100.0`
- multi-shot consistency CV：`0.27029897624035154`
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
- figures/fig_preprocessing_ablation_summary.png
- figures/fig_fk_spectrum_before_after.png
- figures/fig_fk_filter_effect_on_gather.png
- figures/fig_matched_wavelet_score_comparison.png
- figures/fig_semblance_score_volume_slice.png
- figures/fig_frequency_shift_attribute.png
- figures/fig_geometry_ablation_best_locations.png
- figures/fig_geometry_ablation_uncertainty_spans.png
- figures/fig_multi_attribute_ablation.png
- figures/fig_3d_high_score_components.png
- figures/fig_recommendation_decision_flow.png
- animations/anim_pseudo_wavefield.gif
- reports/report_full_pipeline.md
- reports/report_confidence.md
- reports/report_score_method_comparison.md
- reports/report_depth_prior_sensitivity.md
- reports/report_preprocessing_ablation.md
- reports/report_fk_filter_validation.md
- reports/report_matched_wavelet_validation.md
- reports/report_semblance_validation.md
- reports/report_frequency_shift_attribute.md
- reports/report_geometry_ablation.md
- reports/report_multi_attribute_ablation.md

## 导出记录

- 已复制精选文件数量：`46`
- 缺失精选文件数量：`0`

## 当前限制

本目录只保存本轮最新、最值得人工检查的精选结果。时间戳运行目录保留完整本地结果，但大型数组、快照和中间产物默认不纳入 Git。当前定位和置信度仍是科研算法原型诊断，不能作为工程确诊结论。
