# 基础置信度诊断报告

## 指标摘要

- peak sharpness：`1.268`
- local background mean：`0.01127`
- score contrast：`17.4`
- score percentile：`100.00%`
- multi-shot consistency mean：`0.01513`
- multi-shot consistency std：`0.004725`
- multi-shot consistency CV：`0.3123`
- y-depth coupling warning：`False`
- confidence flag：`medium`

## y-depth 耦合检查

- best_x：`60.0` m
- 高分阈值：`0.9` × best_score
- 高分点数量：`19`
- y 跨度：`9.0` m
- depth 跨度：`0.5` m
- 诊断：当前 best_x 切片未触发 y-depth 耦合跨度阈值，但仍需结合图件人工检查。

## 解释边界

这些指标只用于 Stage 3 科研原型的结果自检。它们能够提示峰值是否集中、多炮贡献是否均衡、单侧 DAS-like 几何下是否存在 y-depth 耦合风险，但不能替代完整置信度体系，也不能作为工程确诊结论。
