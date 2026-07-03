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
- `best_depth_at_boundary_warning`：主 best 深度位于扫描上下边界时触发；
- `wide_y_high_score_zone_warning`：best_x 附近高分区 y 跨度过宽时触发；
- `raw_weighted_divergence_warning`：raw_best 与 weighted_best 三维差异过大时触发；
- `shallow_bias_warning`：weighted_best 明显比 raw_best 更浅时触发。

输出文件：

- `arrays/arr_confidence_metrics.json`
- `figures/fig_confidence_diagnostics.png`
- `reports/report_confidence.md`

Stage 3B/3C 还输出：

- `figures/fig_raw_vs_weighted_best_location.png`
- `figures/fig_raw_vs_weighted_x_depth_slice.png`
- `figures/fig_y_high_score_width_check.png`
- `figures/fig_score_method_depth_comparison.png`
- `figures/fig_3d_high_score_uncertainty_summary.png`
- `figures/fig_x_y_depth_uncertainty_slices.png`
- `reports/report_score_method_comparison.md`

## unweighted score 与 weighted score

`score_volume_unweighted` 表示不加 Rayleigh 深度权重的当前 score_method 得分；`score_volume_depth_weighted` 表示乘以 `exp(-h / penetration_depth)` 后的得分；`score_volume_active` 表示当前展示主结果。为了兼容旧测试和旧脚本，`score_volume_raw` 仍保留为 `score_volume_unweighted` 的别名。

若 weighted_best 比 unweighted_best 明显更浅，尤其贴近 `scan_depth_min_m`，报告会触发 shallow/boundary warning。这说明深度先验可能影响了最佳深度，不能把 weighted_best 当作稳定深度估计。

## 推荐位置与三维不确定性

Stage 3C 新增 `recommended_location`、`recommended_location_type` 和 `recommended_location_reason`。当 weighted_best 贴边且 unweighted/weighted 分歧明显时，推荐结果会退化为 `uncertainty_interval`，即用三维高分区的 x/y/depth 范围表达候选体，而不是输出一个确定点。

三维高分区定义为：

```text
score_volume_active >= confidence_threshold_ratio * best_score
```

输出包括：

- `x_span_m`
- `y_span_m`
- `depth_span_m`
- `high_score_region_point_count`
- `high_score_region_volume_estimate_m3`
- `equivalent_uncertainty_box`

这些指标是科研原型阶段的自检工具，不是统计显著性检验、不是完整置信区间，也不能作为工程确诊。

## 绕射走时曲线

Rayleigh-wave diffraction 类方法更核心的是绕射走时曲线，以及直达面波压制后的残余绕射能量。`fig_diffraction_travel_time_curves.png` 用于检查真值和 best_location 的理论绕射曲线是否与炮集中的能量事件大致对应。

后续仍需要做更完整的置信度体系、鲁棒性参数扫描、速度模型敏感性分析和局部全波场验证。
# 历史阶段提示

本文件包含 Stage 3/Stage 4 的扫描和规则型置信度说明，不代表当前完整主线。Stage 5A 已新增 layered/heterogeneous velocity、velocity model ablation 和 model mismatch。当前主线请以 `README.md`、`docs/current_status.md`、`docs/current_algorithm_boundary.md` 和 `code/current_3d_algorithm/` 为准。
