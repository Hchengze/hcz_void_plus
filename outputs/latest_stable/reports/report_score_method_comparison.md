# score_method 轻量对比报告

本报告只比较同一数据、同一扫描网格下的 score_method，不是大规模鲁棒性扫描。

| score_method | unweighted_best | weighted_best | unweighted_error_m | weighted_error_m | weighted_depth_at_boundary |
|---|---|---|---:|---:|---|
| diffraction_energy_stack | x=60.0, y=10.0, h=2.5 | x=60.0, y=10.0, h=0.5 | 1.118 | 2.693 | True |
| normalized_energy_stack | x=60.0, y=10.0, h=2.5 | x=60.0, y=10.0, h=0.5 | 1.118 | 2.693 | True |

## 深度稳定性参考

- best_unweighted_depth_method：`diffraction_energy_stack`
- best_unweighted_depth_abs_error_m：`0.5`
- 说明：仅比较当前场景下 unweighted_best 的深度误差，不代表通用优劣。

当前对比仍基于运动学 DAS-like 数据，不能作为工程确诊。