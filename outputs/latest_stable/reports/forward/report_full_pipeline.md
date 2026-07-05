# Full Pipeline 综合报告

本次运行完成：DAS-like 运动学多炮正演、三维观测几何诊断、基础预处理、多属性 x-y-h 扫描定位、深度先验敏感性诊断和规则型稳定性自检。

## 当前近似条件

- active forward engine：`layered_kinematic`
- forward：`layered_kinematic straight-ray kinematic approximation`
- DAS-like：`DAS-like response approximation`
- velocity：`layered`，支持 uniform / layered / lateral gradient / localized low velocity zone
- velocity approximation：`straight-ray kinematic approximation`，不是弹性波速度反演
- acoustic2d_prototype：只用于 acoustic wave-equation infrastructure validation，不是 Rayleigh 波正演
- elastic2d：下一阶段 Rayleigh/free-surface/void scattering 的核心局部全波场方向
- surface response：`kinematic_surface_response_snapshot`，只是 Rayleigh 波走时控制的地表响应示意，不是真实弹性波模拟
- Rayleigh depth sensitivity：`exp(-h / penetration_depth)` 简化权重，不是严格模态深度核

## 扫描结果

- score method：`diffraction_energy_stack`
- score volume shape：`(41, 9, 8)`
- arr_score_volume.npy 当前主结果：`multi_attribute_unweighted`
- active score kind：`multi_attribute_unweighted`
- scan score mode：`multi_attribute`
- scan depth weighting：`True`
- best_location：x=`60.0` m，y=`6.0` m，h=`2.5` m
- truth_error distance：`3.0413812651491097` m

## raw 与 weighted best 对比

- unweighted_best：x=`60.0` m，y=`6.0` m，h=`2.5` m
- weighted_best：x=`60.0` m，y=`6.0` m，h=`2.5` m
- unweighted -> weighted 差异：dx=`0.0` m，dy=`0.0` m，dh=`0.0` m，三维距离=`0.0` m
- depth_prior_bias_warning：`False`

## 推荐位置与三维不确定性

- recommended_location_type：`multi_region_uncertainty`
- recommended_location：`{'x_m': 60.0, 'y_m': 6.0, 'depth_m': 2.5, 'x_interval_m': [56.0, 64.0], 'y_interval_m': [4.0, 16.0], 'depth_interval_m': [2.5, 3.5], 'component_boxes': [{'point_count': 12, 'x_min_m': 56.0, 'x_max_m': 64.0, 'y_min_m': 4.0, 'y_max_m': 14.0, 'depth_min_m': 2.5, 'depth_max_m': 3.5, 'x_span_m': 8.0, 'y_span_m': 10.0, 'depth_span_m': 1.0}, {'point_count': 1, 'x_min_m': 56.0, 'x_max_m': 56.0, 'y_min_m': 6.0, 'y_max_m': 6.0, 'depth_min_m': 3.5, 'depth_max_m': 3.5, 'x_span_m': 0.0, 'y_span_m': 0.0, 'depth_span_m': 0.0}, {'point_count': 1, 'x_min_m': 60.0, 'x_max_m': 60.0, 'y_min_m': 16.0, 'y_max_m': 16.0, 'depth_min_m': 3.5, 'depth_max_m': 3.5, 'x_span_m': 0.0, 'y_span_m': 0.0, 'depth_span_m': 0.0}]}`
- recommended_reason：weighted_best 受到深度权重影响，或触发边界、宽 y、unweighted-weighted 分歧等 warning；因此不把 weighted_best 作为单点推荐，而采用 unweighted_best 作为参考点，并以三维高分区区间表达不确定性。 高分区存在多个分离连通团块，应表达为候选区集合。
- depth uncertainty interval：`[2.5, 3.5]` m
- 3D high-score span：x=`8.0` m，y=`12.0` m，depth=`1.0` m

## 基础置信度分析

- peak sharpness：`1.397`
- score contrast：`4.274`
- score percentile：`100.00%`
- multi-shot consistency CV：`0.1368`
- y-depth coupling warning：`False`
- best_depth_at_boundary_warning：`False`
- wide_y_high_score_zone_warning：`True`
- raw_weighted_divergence_warning：`False`
- shallow_bias_warning：`False`
- confidence flag：`medium-low`

这些指标只是规则型科研诊断，用于帮助人工判断结果是否稳定，不能作为工程确诊。

## Stage 4B 有效性验证

本轮额外输出预处理消融、FK 滤波验证、matched wavelet、semblance、frequency shift、多属性消融、三维几何消融、三维高分区连通域和推荐决策流程图。若这些验证没有改善 y/depth 不确定性，报告必须解释为“接口已建立，效果待验证”，不能把候选点写成工程确诊。

## Stage 5A 速度模型升级

本轮新增 layered / lateral_gradient / localized_low_velocity_zone / layered_with_anomaly_perturbation 速度模型，并输出 velocity model ablation 与 model mismatch 报告。分层和非均匀速度会改变绕射走时曲线与扫描结果，但当前仍是 straight-ray kinematic approximation，不是 3D elastic wavefield。

## Stage 5B/5C 正演技术路线

Stage 5B 确立 F0-F6 forward roadmap：F0 `kinematic_baseline` 保留为快速基线；F1 `layered_kinematic` 是当前主定位 forward；F2 `acoustic2d_prototype` 只验证声学波动方程框架。Stage 5C 新增 F3 `elastic2d_prototype` 最小 velocity-stress 验证，用于 Rayleigh-like surface event、free-surface 和 void-like scattering 的局部科研检查；F4-F6 面向多剖面 elastic、小域 3D elastic 和外部 solver adapters。

## 风险提示

单侧 DAS-like 几何下 y-depth 可能耦合。best_location 是运动学局部能量聚焦结果，不能作为工程确诊结论。
