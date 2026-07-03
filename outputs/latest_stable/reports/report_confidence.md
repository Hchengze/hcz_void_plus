# 基础置信度诊断报告

## 指标摘要

- peak sharpness：`2.06`
- local background mean：`16.64`
- score contrast：`8.188`
- score percentile：`100.00%`
- multi-shot consistency mean：`101.7`
- multi-shot consistency std：`13.01`
- multi-shot consistency CV：`0.1279`
- y-depth coupling warning：`False`
- best depth at boundary warning：`False`
- wide y high-score zone warning：`True`
- raw/weighted divergence warning：`False`
- shallow bias warning：`False`
- confidence flag：`medium-low`

## unweighted 与 weighted best 对比

- unweighted_best：x=`60.0` m，y=`10.0` m，h=`2.5` m
- weighted_best：x=`60.0` m，y=`10.0` m，h=`2.5` m
- unweighted -> weighted 差异：dx=`0.0` m，dy=`0.0` m，dh=`0.0` m，三维距离=`0.0` m

## 推荐位置表达

- recommended_location_type：`uncertainty_interval`
- recommended_location：`{'x_m': 60.0, 'y_m': 10.0, 'depth_m': 2.5, 'x_interval_m': [60.0, 60.0], 'y_interval_m': [8.0, 12.0], 'depth_interval_m': [2.5, 2.5], 'component_boxes': [{'point_count': 3, 'x_min_m': 60.0, 'x_max_m': 60.0, 'y_min_m': 8.0, 'y_max_m': 12.0, 'depth_min_m': 2.5, 'depth_max_m': 2.5, 'x_span_m': 0.0, 'y_span_m': 4.0, 'depth_span_m': 0.0}]}`
- depth uncertainty interval：`[2.5, 2.5]` m
- recommended reason：weighted_best 受到深度权重影响，或触发边界、宽 y、unweighted-weighted 分歧等 warning；因此不把 weighted_best 作为单点推荐，而采用 unweighted_best 作为参考点，并以三维高分区区间表达不确定性。

## 三维高分区统计

- high score threshold：`0.9` × best_score
- high score point count：`3`
- high score component count：`1`
- multi region warning：`False`
- x span：`0.0` m
- y span：`4.0` m
- depth span：`0.0` m
- equivalent uncertainty box：`{'x_min_m': 60.0, 'x_max_m': 60.0, 'y_min_m': 8.0, 'y_max_m': 12.0, 'depth_min_m': 2.5, 'depth_max_m': 2.5}`

## Stage 3B 新增 warning

- best depth 位于扫描边界：`False`
- best_x 高分区 y 跨度：`4.0` m
- raw/weighted 位置分歧：`False`
- 深度先验偏置：`False`
- weighted 浅部偏置：`False`
- 诊断文字：best_x 附近高分区 y 跨度过宽，横向位置存在不确定性。

## y-depth 耦合检查

- best_x：`60.0` m
- 高分阈值：`0.9` × best_score
- 高分点数量：`3`
- y 跨度：`4.0` m
- depth 跨度：`0.0` m
- 诊断：当前 best_x 切片未触发 y-depth 耦合跨度阈值，但仍需结合图件人工检查。

## 解释边界

这些指标只用于 Stage 3B 科研原型的结果自检。它们能够提示峰值是否集中、多炮贡献是否均衡、深度是否贴边、raw/weighted 是否分歧，以及单侧 DAS-like 几何下是否存在 y-depth 或宽 y 高分区风险，但不能替代完整置信度体系，也不能作为工程确诊结论。
