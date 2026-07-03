# latest_stable 稳定成果摘要

## 本轮信息

- commit id：`82ee9a7`
- 任务名称：`Stage 3 基础置信度指标 + 稳定成果输出管理`
- 运行时间：`2026-07-03T13:49:59`
- 来源目录：`outputs\stage3_run_20260703_134954`

## 当前近似条件

- `kinematic approximation`
- `DAS-like response approximation`
- `kinematic_surface_response`，不是真实弹性波场模拟
- Rayleigh 深度权重是 `exp(-h / penetration_depth)` 简化近似，不是严格模态深度核

## 最佳定位结果

- best_location：x=`60.0` m，y=`6.0` m，h=`0.5` m
- truth_error：`3.905124837953327` m

## 基础置信度指标

- peak sharpness：`1.267805470143464`
- score contrast：`17.40276005710644`
- score percentile：`100.0`
- multi-shot consistency CV：`0.31228140955207195`
- y-depth coupling warning：`False`
- low confidence flag：`medium`

## 推荐人工重点查看

- figures/fig_geometry_layout_check.png
- figures/fig_source_anomaly_receiver_path_section.png
- figures/fig_rayleigh_depth_sensitivity.png
- figures/fig_shot_gather_000.png
- figures/fig_diffraction_travel_time_curves.png
- figures/fig_scan_x_depth_slice.png
- figures/fig_scan_x_y_slice.png
- figures/fig_best_location_map.png
- figures/fig_confidence_diagnostics.png
- animations/anim_pseudo_wavefield.gif
- reports/report_full_pipeline.md
- reports/report_confidence.md

## 导出记录

- 已复制精选文件数量：`14`
- 缺失精选文件数量：`0`

## 当前限制

本目录只保存本轮最新、最值得人工检查的精选结果。时间戳运行目录保留完整本地结果，但大型数组、快照和中间产物默认不纳入 Git。当前定位和置信度仍是科研算法原型诊断，不能作为工程确诊结论。
