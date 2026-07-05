# manual review readiness 报告

本报告检查 Stage 5J 的人工复查入口是否清晰、受控、真实存在。

- stage：`Stage 5J`
- manual_review_figures 数量：`11`
- manual_review_animations 数量：`2`
- 关键三维图齐全：`False`
- 关键动图齐全：`True`
- 状态：`fail`

## 人工建议查看顺序

1. `figures/error_analysis/fig_stage5j_status_badge.png`
2. `figures/forward/fig_geometry_3d_overview.png`
3. `figures/forward/fig_volume_wavefield_xyz_slices.png`
4. `figures/forward/fig_volume_wavefield_3d_energy_proxy.png`
5. `figures/forward/fig_shot_gather_with_velocity_model.png`
6. `figures/forward/fig_shot_gather_attenuation_comparison.png`
7. `figures/localization/fig_3d_uncertainty_ellipsoid.png`
8. `figures/error_analysis/fig_rayleigh_pick_interpretation.png`
9. `animations/forward/anim_single_shot_volume_wavefield.gif`
10. `animations/forward/anim_multishot_forward_overview.gif`

## 动图大小

- `animations/forward/anim_single_shot_volume_wavefield.gif`：`223027` bytes
- `animations/forward/anim_multishot_forward_overview.gif`：`509774` bytes

## warnings

- 无

## failures

- manual_review_figures 数量为 11，应控制在 8-10 张。
- manual_review_figures 缺少关键三维图：['figures/error_analysis/fig_forward_localization_consistency.png', 'figures/localization/fig_3d_posterior_volume.png']

## 解释边界

这些图件表达三维几何与定位表达、三维运动学定位结果，不代表当前 elastic2d 已经是三维弹性正演。