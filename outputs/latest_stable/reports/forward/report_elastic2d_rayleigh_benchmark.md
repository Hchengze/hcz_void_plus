# elastic2d Rayleigh benchmark 报告

本报告比较 collocated 与 staggered 最小 elastic2d validation。它不替代 layered_kinematic 主定位 forward。

- case_count：`8`
- best_case：`staggered_traction_variant`
- best_detected_case：`None`
- rayleigh_like_event_detected：`False`
- rayleigh_velocity_relative_error：`0.2028480598664669`
- best_source_type：`horizontal_force`
- best_free_surface_mode：`stress_zero_variant`
- best_boundary_mode：`sponge_medium`
- ready_for_2p5d：`False`
- picked_event_interpretation：`likely_boundary_reflection_or_late_surface_coda`
- likely_surface_wave_score：`0.18860776053413242`
- likely_boundary_reflection_score：`0.25`
- likely_body_wave_score：`0.2`
- late_coda_score：`0.2`
- failure_reason_ranked：`['boundary_reflection', 'body_wave_or_direct_leakage', 'late_coda_or_grid_dispersion', 'surface_wave_candidate']`

| case | scheme | source | free_surface | boundary | velocity | expected | rel_error | detected | boundary_reflection |
|---|---|---|---|---|---:|---|---:|---|---:|
| collocated_vertical | collocated | vertical_force | approximate | sponge_medium | 174.9 | [212.5, 245.0] | 0.2352 | False | 0.4511 |
| collocated_horizontal | collocated | horizontal_force | approximate | sponge_medium | 175 | [212.5, 245.0] | 0.235 | False | 0.3443 |
| collocated_stress_zero | collocated | horizontal_force | stress_zero_variant | sponge_medium | 174.4 | [212.5, 245.0] | 0.2375 | False | 0.1969 |
| collocated_sponge_weak | collocated | horizontal_force | approximate | sponge_weak | 175 | [212.5, 245.0] | 0.235 | False | 0.342 |
| staggered_vertical | staggered | vertical_force | approximate | sponge_medium | 172.9 | [212.5, 245.0] | 0.2439 | False | 0.2917 |
| staggered_horizontal | staggered | horizontal_force | approximate | sponge_medium | 175 | [212.5, 245.0] | 0.2349 | False | 0.2904 |
| staggered_traction_variant | staggered | horizontal_force | stress_zero_variant | sponge_medium | 275.2 | [212.5, 245.0] | 0.2028 | False | 0 |
| staggered_sponge_weak | staggered | horizontal_force | approximate | sponge_weak | 175 | [212.5, 245.0] | 0.2349 | False | 0.2868 |

## 结论边界

最佳 case 仍不算通过，因为拾取速度没有落入保守 Rayleigh-like 速度范围，且误差仍高于当前 sanity check 门槛。
当前拾取更可能是表面事件、体波泄漏、边界反射和尾波/网格频散的混合结果；具体排序见 failure_reason_ranked。
速度偏差可能同时来自 free surface 近似、海绵边界反射、拾取窗口和小网格频散；下一步优先加固 free surface 与 PML，再做 source/receiver 标定。
若 rayleigh_like_event_detected=False，则不得进入 2.5D 或把 elastic2d 写成 Rayleigh 正演成功。
staggered-grid 本轮只是 benchmark validation engine，不是工业级模拟。