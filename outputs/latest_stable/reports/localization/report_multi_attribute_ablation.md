# 多属性评分消融报告

| group | best | y_span_m | depth_span_m | components | flag |
|---|---|---:|---:|---:|---|
| energy_only | x=60.0, y=10.0, h=2.5, error=1.118033988749895 | 4 | 0 | 1 | low |
| normalized_energy_only | x=60.0, y=10.0, h=2.5, error=1.118033988749895 | 4 | 0 | 1 | low |
| matched_wavelet_only | x=60.0, y=10.0, h=3.5, error=1.118033988749895 | 8 | 0 | 1 | low |
| semblance_only | x=172.0, y=4.0, h=1.5, error=112.12158578971312 | 16 | 0 | 2 | low |
| energy_matched_wavelet | x=60.0, y=10.0, h=2.5, error=1.118033988749895 | 8 | 0 | 1 | low |
| energy_matched_wavelet_semblance | x=60.0, y=10.0, h=2.5, error=1.118033988749895 | 4 | 0 | 1 | low |
| full_multi_attribute | x=60.0, y=10.0, h=2.5, error=1.118033988749895 | 4 | 0 | 1 | low |

- best_group_by_truth_error: `energy_only`
- full_multi_attribute_improved_over_energy: `False`

若 full_multi_attribute 未优于 energy_only，应在报告中诚实说明当前多属性框架尚未证明优于 energy stack。