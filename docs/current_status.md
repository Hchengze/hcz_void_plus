# 当前状态：Stage 5D

## 最新事实

1. Stage 5C 已完成并推送，当前进入 Stage 5D。
2. 当前定位结果仍应表达为 `uncertainty_interval` 或三维候选体，不应写成确定工程诊断点。
3. 预处理中 `taper direct mute`、`trace normalization` 和 bandpass 对绕射识别有明显作用。
4. FK / f-v 速度扇区滤波当前增强有限，更适合作为 QC 和后续增强接口。
5. matched wavelet 与 semblance 可以收缩部分高分区，但尚未稳定证明单点误差优于 energy。
6. frequency shift 已成为最小可用诊断属性，但默认不参与主定位。
7. two-side sources 在 Stage 4B 几何消融中对 y 约束改善最明显。
8. y-depth 可分辨性仍是瓶颈。
9. Stage 5A 默认速度模型升级到 `layered`，但仍是 straight-ray kinematic approximation。
10. Stage 5B 已确立 forward roadmap：F1 `layered_kinematic` 为当前主线，F2 `acoustic2d_prototype` 只作 validation。
11. Stage 5C 新增 `elastic2d_prototype`，作为 Rayleigh-like surface event、free-surface 和 void-like scattering 的局部物理验证起点。
12. Stage 5C 对 `outputs/latest_stable/` 做分层精选治理，根目录不再堆积所有历史阶段图件。
13. Stage 5D 新增 repository health、figure self-check、velocity model audit 和当前速度模型可视化，避免旧图、重复图或错误阶段图件混入 latest_stable。
14. Stage 5D 继续加固 elastic2d 的 Rayleigh-like 拾取、void residual 参数敏感性、DAS-like gauge length response 和 elastic-vs-kinematic 能量解释比例。
15. 真实道路场景中，正演真实性、速度模型不确定性、观测几何和 y-depth 耦合必须一起讨论。

## 当前默认主线

- 稳定代码区：`code/current_3d_algorithm/`
- 当前正演主线：`layered_kinematic`
- validation forward：`acoustic2d_prototype`、`elastic2d_prototype`
- 下一步物理正演：`elastic2d_prototype` 精度和稳定性硬化、2.5D 多剖面验证
- 默认速度模型：`layered`
- Stage 5D 速度模型核验：direct / scatter / scan 都必须经过 velocity_model travel-time 接口
- Stage 5D 图件导出：进入 `latest_stable` 前必须通过 figure self-check
- 主定位：`multi_attribute_unweighted`
- depth weighting：辅助诊断，不默认主导定位
- 输出表达：三维高分候选体 + 不确定性区间 + 连通域诊断

## 人工检查入口

优先查看：

- `outputs/latest_stable/summary.md`
- `outputs/latest_stable/figures/core/fig_confidence_diagnostics.png`
- `outputs/latest_stable/figures/forward/fig_forward_engine_comparison.png`
- `outputs/latest_stable/figures/forward/fig_forward_roadmap_status.png`
- `outputs/latest_stable/figures/forward/fig_acoustic2d_wavefield_snapshots.png`
- `outputs/latest_stable/figures/forward/fig_elastic2d_rayleigh_wavefield_snapshots.png`
- `outputs/latest_stable/figures/forward/fig_elastic2d_void_scattering_residual.png`
- `outputs/latest_stable/figures/forward/fig_elastic2d_rayleigh_pick_diagnostics.png`
- `outputs/latest_stable/figures/forward/fig_elastic2d_das_component_comparison.png`
- `outputs/latest_stable/figures/diagnostics/fig_velocity_model_active_badge.png`
- `outputs/latest_stable/figures/diagnostics/fig_velocity_model_profile_current.png`
- `outputs/latest_stable/figures/diagnostics/fig_velocity_model_comparison.png`
- `outputs/latest_stable/figures/diagnostics/fig_model_mismatch_error_summary.png`
- `outputs/latest_stable/reports/core/report_repository_health.md`
- `outputs/latest_stable/reports/core/report_figure_self_check.md`
- `outputs/latest_stable/reports/forward/report_forward_engine_ablation.md`
- `outputs/latest_stable/reports/forward/report_acoustic2d_prototype.md`
- `outputs/latest_stable/reports/forward/report_elastic2d_rayleigh_validation.md`
- `outputs/latest_stable/reports/forward/report_elastic2d_void_scattering.md`
- `outputs/latest_stable/reports/diagnostics/report_velocity_model_ablation.md`
- `outputs/latest_stable/reports/diagnostics/report_model_mismatch.md`
