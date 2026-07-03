# Full Pipeline 综合报告

本次运行完成：DAS-like 运动学多炮正演、中文图件、运动学地表响应示意图/GIF、直达波预测、基础 x-y-h 多炮扫描定位和 Stage 3 基础置信度诊断。

## 当前近似条件

- forward：`kinematic approximation`
- DAS-like：`DAS-like response approximation`
- velocity：`uniform effective Rayleigh velocity`
- surface response：`kinematic_surface_response_snapshot`，只是 Rayleigh 波走时控制的地表响应示意，不是真实弹性波模拟
- Rayleigh depth sensitivity：`exp(-h / penetration_depth)` 简化权重，不是严格模态深度核

## 扫描结果

- score method：`diffraction_energy_stack`
- score volume shape：`(81, 17, 16)`
- arr_score_volume.npy 当前主结果：`depth_weighted`
- scan depth weighting：`True`
- best_location：x=`60.0` m，y=`9.0` m，h=`0.5` m
- truth_error distance：`2.5` m

## raw 与 weighted best 对比

- raw_best：x=`60.0` m，y=`9.0` m，h=`2.5` m
- weighted_best：x=`60.0` m，y=`9.0` m，h=`0.5` m
- raw -> weighted 差异：dx=`0.0` m，dy=`0.0` m，dh=`-2.0` m，三维距离=`2.0` m
- depth_prior_bias_warning：`True`

## 基础置信度分析

- peak sharpness：`1.107`
- score contrast：`7.2`
- score percentile：`100.00%`
- multi-shot consistency CV：`0.2073`
- y-depth coupling warning：`False`
- best_depth_at_boundary_warning：`True`
- wide_y_high_score_zone_warning：`True`
- raw_weighted_divergence_warning：`True`
- shallow_bias_warning：`True`
- confidence flag：`low`

这些指标只是规则型科研诊断，用于帮助人工判断结果是否稳定，不能作为工程确诊。

## 风险提示

单侧 DAS-like 几何下 y-depth 可能耦合。best_location 是运动学局部能量聚焦结果，不能作为工程确诊结论。
