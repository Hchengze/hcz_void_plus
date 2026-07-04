# 当前状态：Stage 5F

## 最新事实

1. Stage 5E 已完成并推送，当前进入 Stage 5F。
2. 当前 active velocity model 是 `layered`，不是 `uniform`。
3. 当前 active forward engine 是 `layered_kinematic`，它仍是 straight-ray kinematic approximation。
4. `elastic2d_prototype` 和本轮新增的 staggered-grid elastic2d benchmark 都只属于 validation forward。
5. 当前结果仍应表达为三维高分候选体和不确定性区间，不是工程确诊点。
6. Rayleigh-like benchmark 尚未通过；未通过前 `ready_for_2p5d=False`。
7. DAS-like gauge strain 可以出现非零数值，但当前仍弱且未经过真实 DAS gauge、方向和仪器响应校准，不能默认用于定位。
8. latest_stable 是当前精选成果目录，不是历史图件堆积目录。
9. Stage 5F 新增图件质量检查、重复图检查、语言检查和 curated 清单治理，防止空图、重复图、英文图或旧阶段图进入当前精选。
10. 三维场景仍是项目主问题：`source_xyz / receiver_xyz / candidate_xyz / x-y-depth high-score region` 必须保留。
11. 2D elastic 只是服务三维道路 DAS-like 场景的局部物理验证，不得替代三维 x-y-h 定位。

## 当前默认主线

- 稳定代码区：`code/current_3d_algorithm/`
- 当前主定位 forward：`layered_kinematic`
- validation forward：`acoustic2d_prototype`、`elastic2d_prototype`、`elastic2d_staggered_benchmark`
- 默认速度模型：`layered`
- 主定位：`multi_attribute_unweighted`
- depth weighting：辅助诊断，不默认主导定位
- 输出表达：三维高分候选体 + 不确定性区间 + 连通域诊断
- 2.5D 进入条件：Rayleigh benchmark 通过、DAS gauge response 非零且可解释、void residual 非边界伪影、latest_stable 图件和 summary 一致。

## 人工检查入口

优先查看：

- `outputs/latest_stable/summary.md`
- `outputs/latest_stable/figures/core/fig_stage5f_status_badge.png`
- `outputs/latest_stable/figures/core/fig_confidence_diagnostics.png`
- `outputs/latest_stable/figures/diagnostics/fig_velocity_model_active_badge.png`
- `outputs/latest_stable/figures/diagnostics/fig_latest_stable_quality_summary.png`
- `outputs/latest_stable/figures/forward/fig_elastic2d_rayleigh_benchmark_matrix.png`
- `outputs/latest_stable/figures/forward/fig_elastic2d_rayleigh_velocity_error.png`
- `outputs/latest_stable/figures/forward/fig_elastic2d_surface_event_ridge.png`
- `outputs/latest_stable/figures/forward/fig_elastic2d_das_best_case.png`
- `outputs/latest_stable/figures/localization/fig_scan_x_y_slice.png`
- `outputs/latest_stable/figures/uncertainty/fig_x_y_depth_uncertainty_slices.png`
- `outputs/latest_stable/reports/core/report_latest_stable_file_audit.md`
- `outputs/latest_stable/reports/core/report_figure_quality_check.md`
- `outputs/latest_stable/reports/core/report_figure_deduplication.md`
- `outputs/latest_stable/reports/core/report_figure_language_check.md`
- `outputs/latest_stable/reports/forward/report_elastic2d_rayleigh_benchmark.md`
- `outputs/latest_stable/reports/diagnostics/report_velocity_model_physics_bridge.md`

## 当前限制

- 当前不是完整 DAS 仪器响应。
- 当前不是 3D elastic wavefield。
- 当前异常体仍是 equivalent scatter representation。
- 当前分层速度模型是等效 Rayleigh velocity，不是完整 Vp/Vs/rho 弹性模型。
- 当前 elastic2d 仍是科研验证原型，不是工业级模拟。
- 当前结果是科研候选区，不是工程确诊。
