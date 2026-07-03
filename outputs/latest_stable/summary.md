# latest_stable 稳定成果摘要

## 本轮信息

- commit id：`45f1096`
- 任务名称：`Stage 3B 三维场景约束下的扫描诊断修正与置信度稳健化`
- 运行时间：`2026-07-03T14:24:58`
- 来源目录：`outputs\stage3_run_20260703_142452`

## 当前近似条件

- `kinematic approximation`
- `DAS-like response approximation`
- `kinematic_surface_response`，不是真实弹性波场模拟
- Rayleigh 深度权重是 `exp(-h / penetration_depth)` 简化近似，不是严格模态深度核

## 最佳定位结果

- best_location：x=`60.0` m，y=`9.0` m，h=`0.5` m
- truth_error：`2.5` m

## raw 与 weighted best 对比

- raw_best：x=`60.0` m，y=`9.0` m，h=`2.5` m
- weighted_best：x=`60.0` m，y=`9.0` m，h=`0.5` m
- raw -> weighted 差异：dx=`0.0` m，dy=`0.0` m，dh=`-2.0` m，三维距离=`2.0` m

## 基础置信度指标

- peak sharpness：`1.1066476916547154`
- score contrast：`7.19986793911462`
- score percentile：`100.0`
- multi-shot consistency CV：`0.20730813359265382`
- y-depth coupling warning：`False`
- best depth boundary warning：`True`
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
- animations/anim_pseudo_wavefield.gif
- reports/report_full_pipeline.md
- reports/report_confidence.md

## 导出记录

- 已复制精选文件数量：`17`
- 缺失精选文件数量：`0`

## 当前限制

本目录只保存本轮最新、最值得人工检查的精选结果。时间戳运行目录保留完整本地结果，但大型数组、快照和中间产物默认不纳入 Git。当前定位和置信度仍是科研算法原型诊断，不能作为工程确诊结论。
