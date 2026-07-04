# elastic2d DAS-like gauge response 报告

本报告从 elastic2d surface velocity 近似派生 point receiver 和 gauge-length strain 响应。

- point_receiver_gather 使用 surface vz。
- gauge_length_strain_gather 使用 surface vx 沿 x 方向的 gauge-length finite difference。
- gauge length 会改变局部散射响应，短波长事件可能被增强或削弱。
- point receiver 和 DAS-like strain 不能混为一谈。
- 后续三维 receiver polyline 应沿局部切向方向计算 strain。

- point shape：`(1617, 77)`。
- strain shape：`(1617, 77)`。
- strain_rms / point_rms：`0`。
- best_source_type_for_gauge：`vertical_force`。
- best_gauge_length_m：`0.5`。
- gauge_void_residual_rms：`0.0`。

## Stage 5E 非零响应检查

- das_gauge_nonzero_status：`nonzero`。
- best_velocity_gauge_case：`vertical_force_g0.5`。
- best_velocity_gauge_rms：`5.40751067390065e-09`。
- best_displacement_gauge_case：`vertical_force_g0.5`。
- best_displacement_gauge_rms：`2.160818842329346e-11`。
- default_localization_should_use_gauge_strain：`False`。
- diagnosis：gauge strain 非零，但仍只属于 DAS-like validation，不是真实 DAS 仪器响应。

若 gauge strain 为零或很弱，必须明确禁止默认纳入定位；即使非零，也仍需真实 DAS gauge/方向/仪器响应校准。