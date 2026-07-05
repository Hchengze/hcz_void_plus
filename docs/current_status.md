# 当前状态：Stage 5I

## 最新事实

1. Stage 5H 已完成，当前进入 **Stage 5I：三维运动学正演-定位一致性修复 + 三维多属性反演增强 + 三维不确定性体输出**。
2. 当前 active velocity model 是 `layered`，不是 `uniform`。
3. 当前 active forward engine 是 `layered_kinematic`，它仍是 straight-ray kinematic approximation。
4. `elastic2d_prototype` 与 staggered-grid benchmark 都只属于 validation forward，不替代主定位 forward。
5. 当前结果仍应表达为三维高分候选体、推荐参考位置和不确定性盒子，不是工程确诊点。
6. Rayleigh-like benchmark 尚未通过；未通过前 `ready_for_2p5d=False`。
7. DAS-like gauge strain 统一口径为 `nonzero_but_weak_not_for_default_localization`，不能默认用于定位。
8. latest_stable 是当前精选成果目录，不是历史图件堆积目录。
9. Stage 5I 不再把主要精力放在图件治理上；当前重点是 scan 走时路径积分一致性、三维多属性 score volume、posterior-like volume 和几何分辨率诊断。
10. 三维场景仍是项目主问题：`source_xyz / receiver_xyz / candidate_xyz / x-y-depth high-score region` 必须保留。
11. 2D elastic 只是服务三维道路 DAS-like 场景的局部物理验证，不得替代三维 x-y-h 定位。

## 当前默认主线

- 稳定代码区：`code/current_3d_algorithm/`
- 研发区：`src/`
- 当前主定位 forward：`layered_kinematic`
- validation forward：`acoustic2d_prototype`、`elastic2d_prototype`、`elastic2d_staggered_benchmark`
- 默认速度模型：`layered`
- 主定位：`multi_attribute_unweighted`
- depth weighting：辅助诊断，不默认主导定位
- 输出表达：三维高分候选体 + 推荐参考点 + 三维不确定性盒子
- 2.5D 进入条件：Rayleigh benchmark 通过、DAS gauge response 非零且可解释、void residual 非边界伪影、latest_stable 图件和 summary 一致。

## 人工检查入口

优先查看：

- `outputs/latest_stable/summary.md`
- `outputs/latest_stable/figures/forward/fig_geometry_3d_overview.png`
- `outputs/latest_stable/figures/forward/fig_velocity_model_active_badge.png`
- `outputs/latest_stable/figures/forward/fig_velocity_model_physics_bridge.png`
- `outputs/latest_stable/figures/forward/fig_elastic2d_rayleigh_benchmark_matrix.png`
- `outputs/latest_stable/figures/forward/fig_elastic2d_rayleigh_velocity_error.png`
- `outputs/latest_stable/figures/forward/fig_elastic2d_das_best_case.png`
- `outputs/latest_stable/figures/localization/fig_3d_high_score_region.png`
- `outputs/latest_stable/figures/localization/fig_recommended_location_3d.png`
- `outputs/latest_stable/figures/localization/fig_3d_uncertainty_box.png`
- `outputs/latest_stable/figures/error_analysis/fig_stage5i_status_badge.png`
- `outputs/latest_stable/animations/forward/anim_multishot_forward_overview.gif`
- `outputs/latest_stable/animations/forward/anim_single_shot_wavefield.gif`

## 当前限制

- 当前不是完整 DAS 仪器响应。
- 当前不是 3D elastic wavefield。
- 当前异常体仍是 equivalent scatter representation。
- 当前分层速度模型是等效 Rayleigh velocity，不是完整 Vp/Vs/rho 弹性模型。
- 当前 elastic2d/staggered 仍是科研验证原型，不是工业级模拟。
- 当前结果是科研候选区，不是工程确诊。
