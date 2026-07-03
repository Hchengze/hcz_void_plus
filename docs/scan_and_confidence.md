# Scan And Confidence

Stage 3 已在基础扫描定位之后加入规则型基础置信度诊断，但仍不实现完整概率置信度体系。

## 扫描方法

当前方法为 `diffraction_energy_stack`：

1. 构建候选异常体位置 `x-y-h` 网格；
2. 计算 `source -> candidate -> receiver` 理论散射走时；
3. 在 DAS-like 数据中沿对应走时时间窗提取局部能量；
4. 对所有炮和通道求平均，形成 raw score volume；
5. 可选乘以 Rayleigh 简化深度敏感性权重；
6. 最高得分点作为科研级候选 `best_location`。

## score volume

`score_volume` 是每一个候选异常体位置的扫描得分体，shape 为：

```text
n_x × n_y × n_depth
```

它保存于 `arrays/arr_score_volume.npy`。Stage 2C 同时保存：

- `arrays/arr_score_volume_raw.npy`
- `arrays/arr_score_volume_depth_weighted.npy`

对应网格保存于：

- `arrays/arr_scan_x_grid.npy`
- `arrays/arr_scan_y_grid.npy`
- `arrays/arr_scan_depth_grid.npy`

## 风险提示

单侧 DAS-like 几何下，横向位置 y 和埋深 h 可能耦合。Stage 2 的 best_location 是运动学局部能量聚焦结果，不能作为工程确诊结论。

## Stage 3 基础置信度指标

当前实现以下可解释指标：

- `peak_sharpness`：最高峰相对局部邻域背景的比值，用于判断峰是否集中；
- `score_contrast`：最高分相对全局平均得分的比值；
- `score_percentile`：最高分在全部候选点中的百分位；
- `multi-shot consistency`：最佳候选点处每炮贡献均值、标准差和变异系数；
- `y-depth coupling warning`：在 best_x 附近检查 y-depth 高分区是否同时拉长；
- `low_confidence_flag`：按规则输出 `high / medium / low`。

输出文件：

- `arrays/arr_confidence_metrics.json`
- `figures/fig_confidence_diagnostics.png`
- `reports/report_confidence.md`

这些指标是科研原型阶段的自检工具，不是统计显著性检验、不是完整置信区间，也不能作为工程确诊。

## 绕射走时曲线

Rayleigh-wave diffraction 类方法更核心的是绕射走时曲线，以及直达面波压制后的残余绕射能量。`fig_diffraction_travel_time_curves.png` 用于检查真值和 best_location 的理论绕射曲线是否与炮集中的能量事件大致对应。

后续仍需要做更完整的置信度体系、鲁棒性参数扫描、速度模型敏感性分析和局部全波场验证。
