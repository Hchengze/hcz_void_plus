# 基础置信度诊断报告

## 指标摘要

- peak sharpness：`1.107`
- local background mean：`0.03107`
- score contrast：`7.2`
- score percentile：`100.00%`
- multi-shot consistency mean：`0.03642`
- multi-shot consistency std：`0.00755`
- multi-shot consistency CV：`0.2073`
- y-depth coupling warning：`False`
- best depth at boundary warning：`True`
- wide y high-score zone warning：`True`
- raw/weighted divergence warning：`True`
- shallow bias warning：`True`
- confidence flag：`low`

## raw 与 weighted best 对比

- raw_best：x=`60.0` m，y=`9.0` m，h=`2.5` m
- weighted_best：x=`60.0` m，y=`9.0` m，h=`0.5` m
- raw -> weighted 差异：dx=`0.0` m，dy=`0.0` m，dh=`-2.0` m，三维距离=`2.0` m

## Stage 3B 新增 warning

- best depth 位于扫描边界：`True`
- best_x 高分区 y 跨度：`10.0` m
- raw/weighted 位置分歧：`True`
- 深度先验偏置：`True`
- weighted 浅部偏置：`True`
- 诊断文字：best_depth 位于扫描最小深度边界，深度结果不稳定。；best_x 附近高分区 y 跨度过宽，横向位置存在不确定性。；raw_best 与 weighted_best 三维位置差异较大，深度权重对结果影响显著。；weighted_best 明显比 raw_best 更浅，存在 Rayleigh 深度先验浅部偏置。

## y-depth 耦合检查

- best_x：`60.0` m
- 高分阈值：`0.9` × best_score
- 高分点数量：`18`
- y 跨度：`10.0` m
- depth 跨度：`0.5` m
- 诊断：当前 best_x 切片未触发 y-depth 耦合跨度阈值，但仍需结合图件人工检查。

## 解释边界

这些指标只用于 Stage 3B 科研原型的结果自检。它们能够提示峰值是否集中、多炮贡献是否均衡、深度是否贴边、raw/weighted 是否分歧，以及单侧 DAS-like 几何下是否存在 y-depth 或宽 y 高分区风险，但不能替代完整置信度体系，也不能作为工程确诊结论。
