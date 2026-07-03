# 基础置信度诊断报告

## 指标摘要

- peak sharpness：`1.115`
- local background mean：`33.78`
- score contrast：`5.448`
- score percentile：`100.00%`
- multi-shot consistency mean：`112.1`
- multi-shot consistency std：`31.35`
- multi-shot consistency CV：`0.2796`
- y-depth coupling warning：`True`
- best depth at boundary warning：`False`
- wide y high-score zone warning：`True`
- raw/weighted divergence warning：`True`
- shallow bias warning：`True`
- confidence flag：`low`

## unweighted 与 weighted best 对比

- unweighted_best：x=`60.0` m，y=`9.0` m，h=`2.5` m
- weighted_best：x=`60.0` m，y=`9.0` m，h=`0.5` m
- unweighted -> weighted 差异：dx=`0.0` m，dy=`0.0` m，dh=`-2.0` m，三维距离=`2.0` m

## 推荐位置表达

- recommended_location_type：`uncertainty_interval`
- recommended_location：`{'x_m': 60.0, 'y_m': 9.0, 'depth_m': 2.5, 'x_interval_m': [60.0, 60.0], 'y_interval_m': [6.0, 13.0], 'depth_interval_m': [0.5, 6.0]}`
- depth uncertainty interval：`[0.5, 6.0]` m
- recommended reason：weighted_best 受到深度权重影响且触发边界/宽 y/unweighted-weighted 分歧等 warning；因此不把 weighted_best 作为单点推荐，而采用 unweighted_best 作为参考点，并以三维高分区区间表达不确定性。

## 三维高分区统计

- high score threshold：`0.9` × best_score
- high score point count：`87`
- x span：`0.0` m
- y span：`7.0` m
- depth span：`5.5` m
- equivalent uncertainty box：`{'x_min_m': 60.0, 'x_max_m': 60.0, 'y_min_m': 6.0, 'y_max_m': 13.0, 'depth_min_m': 0.5, 'depth_max_m': 6.0}`

## Stage 3B 新增 warning

- best depth 位于扫描边界：`False`
- best_x 高分区 y 跨度：`7.0` m
- raw/weighted 位置分歧：`True`
- 深度先验偏置：`True`
- weighted 浅部偏置：`True`
- 诊断文字：best_x 附近高分区 y 跨度过宽，横向位置存在不确定性。；raw_best 与 weighted_best 三维位置差异较大，深度权重对结果影响显著。；weighted_best 明显比 raw_best 更浅，存在 Rayleigh 深度先验浅部偏置。

## y-depth 耦合检查

- best_x：`60.0` m
- 高分阈值：`0.9` × best_score
- 高分点数量：`87`
- y 跨度：`7.0` m
- depth 跨度：`5.5` m
- 诊断：y-depth 高分区同时沿横向和深度方向展开，单侧 DAS-like 几何耦合风险较高。

## 解释边界

这些指标只用于 Stage 3B 科研原型的结果自检。它们能够提示峰值是否集中、多炮贡献是否均衡、深度是否贴边、raw/weighted 是否分歧，以及单侧 DAS-like 几何下是否存在 y-depth 或宽 y 高分区风险，但不能替代完整置信度体系，也不能作为工程确诊结论。
