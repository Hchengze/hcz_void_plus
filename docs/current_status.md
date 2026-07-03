# 当前状态：Stage 5A

## 最新事实

1. Stage 4B 已完成并推送，当前进入 Stage 5A。
2. 当前定位结果仍应表达为 `uncertainty_interval` 或三维候选体，不应写成确定工程诊断点。
3. 预处理中 `taper direct mute`、`trace normalization` 和 bandpass 对绕射识别有明显作用。
4. FK / f-v 速度扇区滤波当前增强有限，更适合作为 QC 和后续增强接口。
5. matched wavelet 与 semblance 可以收缩部分高分区，但尚未稳定证明单点误差优于 energy。
6. frequency shift 已成为最小可用诊断属性，但默认不参与主定位。
7. two-side sources 在 Stage 4B 几何消融中对 y 约束改善最明显。
8. y-depth 可分辨性仍是瓶颈。
9. 均匀速度模型是物理真实性短板，Stage 5A 默认升级到 layered。
10. 真实道路场景中，速度模型不确定性、观测几何和 y-depth 耦合必须一起讨论。

## 当前默认主线

- 稳定代码区：`code/current_3d_algorithm/`
- 默认速度模型：`layered`
- 主定位：`multi_attribute_unweighted`
- depth weighting：辅助诊断，不默认主导定位
- 输出表达：三维高分候选体 + 不确定性区间 + 连通域诊断

## 人工检查入口

优先查看：

- `outputs/latest_stable/summary.md`
- `outputs/latest_stable/figures/fig_velocity_model_comparison.png`
- `outputs/latest_stable/figures/fig_model_mismatch_error_summary.png`
- `outputs/latest_stable/reports/report_velocity_model_ablation.md`
- `outputs/latest_stable/reports/report_model_mismatch.md`
