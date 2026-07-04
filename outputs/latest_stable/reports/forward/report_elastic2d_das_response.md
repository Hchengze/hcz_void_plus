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