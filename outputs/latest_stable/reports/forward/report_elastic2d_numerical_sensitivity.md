# elastic2d 数值敏感性报告

本报告比较 source、source depth、sponge、free-surface 和 receiver depth 对 Rayleigh-like 拾取的影响。
所有结果仅服务 validation forward；layered_kinematic 仍是当前主定位 forward。

- case_count：`9`
- best_case：`source_horizontal`
- best estimated velocity：`174.99252279465844` m/s
- expected range：`[212.5, 245.0]` m/s
- rayleigh_like_event_detected_any：`False`
- likely_failure_cause：`boundary_reflection_or_late_coda`
- elastic2d_ready_for_2p5d：`False`

| case | source | depth | sponge | free_surface | receiver | velocity | detected | body leakage | boundary reflection |
|---|---|---:|---|---|---|---:|---|---:|---:|
| baseline_vertical_depth0.2_medium_approx_surface | vertical_force | 0.2 | medium | approximate | surface | 174.9 | False | 2.067e-12 | 0.4511 |
| source_horizontal | horizontal_force | 0.2 | medium | approximate | surface | 175 | False | 3.4e-11 | 0.3443 |
| source_explosive | explosive | 0.2 | medium | approximate | surface | 175 | False | 4.39e-11 | 0.1738 |
| source_depth0.1 | vertical_force | 0.1 | medium | approximate | surface | 174.3 | False | 9.455e-11 | 0.2204 |
| source_depth0.4 | vertical_force | 0.4 | medium | approximate | surface | 174.9 | False | 6.004e-13 | 0.4651 |
| sponge_weak | vertical_force | 0.2 | weak | approximate | surface | 175 | False | 2.248e-12 | 0.4476 |
| sponge_strong | vertical_force | 0.2 | strong | approximate | surface | 175 | False | 1.972e-12 | 0.4698 |
| free_surface_stress_zero_variant | vertical_force | 0.2 | medium | stress_zero_variant | surface | 174 | False | 9.636e-46 | 0.6333 |
| receiver_one_grid_below | vertical_force | 0.2 | medium | approximate | one_grid_below_surface | 174.5 | False | 1.276e-10 | 0.1436 |

## 解释边界

若 Rayleigh-like 检测未通过，本报告不得被写成 Rayleigh 正演成功。
当前 collocated-grid prototype 的自由表面、sponge 和拾取逻辑仍需继续硬化；未通过前不建议进入 2.5D。