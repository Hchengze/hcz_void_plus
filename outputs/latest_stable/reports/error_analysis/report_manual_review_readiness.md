# manual review readiness 报告

本报告检查 Stage 5I 的人工复查入口是否清晰、受控、真实存在。

- stage：`Stage 5I`
- manual_review_figures 数量：`10`
- manual_review_animations 数量：`2`
- 关键三维图齐全：`True`
- 关键动图齐全：`True`
- 状态：`pass`

## 人工建议查看顺序

1. `figures/error_analysis/fig_stage5i_status_badge.png`
2. `figures/forward/fig_geometry_3d_overview.png`
3. `animations/forward/anim_multishot_forward_overview.gif`
4. `animations/forward/anim_single_shot_wavefield.gif`
5. `figures/forward/fig_velocity_model_active_badge.png`
6. `figures/forward/fig_velocity_model_physics_bridge.png`
7. `figures/forward/fig_elastic2d_rayleigh_benchmark_matrix.png`
8. `figures/forward/fig_elastic2d_das_best_case.png`
9. `figures/localization/fig_3d_high_score_region.png`
10. `figures/localization/fig_recommended_location_3d.png`
11. `figures/localization/fig_3d_uncertainty_box.png`
12. `figures/error_analysis/fig_rayleigh_pick_interpretation.png`

## 动图大小

- `animations/forward/anim_multishot_forward_overview.gif`：`517286` bytes
- `animations/forward/anim_single_shot_wavefield.gif`：`511043` bytes

## warnings

- 无

## failures

- 无

## 解释边界

这些图件表达三维几何与定位表达、三维运动学定位结果，不代表当前 elastic2d 已经是三维弹性正演。