# Full Pipeline 综合报告

本次运行完成：DAS-like 运动学多炮正演、三维观测几何诊断、基础预处理、多属性 x-y-h 扫描定位、深度先验敏感性诊断和规则型稳定性自检。

## 当前近似条件

- forward：`kinematic approximation`
- DAS-like：`DAS-like response approximation`
- velocity：`uniform effective Rayleigh velocity`
- surface response：`kinematic_surface_response_snapshot`，只是 Rayleigh 波走时控制的地表响应示意，不是真实弹性波模拟
- Rayleigh depth sensitivity：`exp(-h / penetration_depth)` 简化权重，不是严格模态深度核

## 扫描结果

- score method：`diffraction_energy_stack`
- score volume shape：`(41, 9, 8)`
- arr_score_volume.npy 当前主结果：`multi_attribute_unweighted`
- active score kind：`multi_attribute_unweighted`
- scan score mode：`multi_attribute`
- scan depth weighting：`True`
- best_location：x=`60.0` m，y=`10.0` m，h=`2.5` m
- truth_error distance：`1.118033988749895` m

## raw 与 weighted best 对比

- unweighted_best：x=`60.0` m，y=`10.0` m，h=`2.5` m
- weighted_best：x=`60.0` m，y=`10.0` m，h=`0.5` m
- unweighted -> weighted 差异：dx=`0.0` m，dy=`0.0` m，dh=`-2.0` m，三维距离=`2.0` m
- depth_prior_bias_warning：`True`

## 推荐位置与三维不确定性

- recommended_location_type：`uncertainty_interval`
- recommended_location：`{'x_m': 60.0, 'y_m': 10.0, 'depth_m': 2.5, 'x_interval_m': [60.0, 60.0], 'y_interval_m': [6.0, 14.0], 'depth_interval_m': [0.5, 5.5], 'component_boxes': [{'point_count': 24, 'x_min_m': 60.0, 'x_max_m': 60.0, 'y_min_m': 6.0, 'y_max_m': 14.0, 'depth_min_m': 0.5, 'depth_max_m': 5.5, 'x_span_m': 0.0, 'y_span_m': 8.0, 'depth_span_m': 5.0}]}`
- recommended_reason：weighted_best 受到深度权重影响，或触发边界、宽 y、unweighted-weighted 分歧等 warning；因此不把 weighted_best 作为单点推荐，而采用 unweighted_best 作为参考点，并以三维高分区区间表达不确定性。
- depth uncertainty interval：`[0.5, 5.5]` m
- 3D high-score span：x=`0.0` m，y=`8.0` m，depth=`5.0` m

## 基础置信度分析

- peak sharpness：`1.434`
- score contrast：`5.424`
- score percentile：`100.00%`
- multi-shot consistency CV：`0.2703`
- y-depth coupling warning：`True`
- best_depth_at_boundary_warning：`False`
- wide_y_high_score_zone_warning：`True`
- raw_weighted_divergence_warning：`True`
- shallow_bias_warning：`True`
- confidence flag：`low`

这些指标只是规则型科研诊断，用于帮助人工判断结果是否稳定，不能作为工程确诊。

## Stage 4B 有效性验证

本轮额外输出预处理消融、FK 滤波验证、matched wavelet、semblance、frequency shift、多属性消融、三维几何消融、三维高分区连通域和推荐决策流程图。若这些验证没有改善 y/depth 不确定性，报告必须解释为“接口已建立，效果待验证”，不能把候选点写成工程确诊。

## 风险提示

单侧 DAS-like 几何下 y-depth 可能耦合。best_location 是运动学局部能量聚焦结果，不能作为工程确诊结论。
