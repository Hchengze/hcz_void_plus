# 速度模型物理关系桥接报告

本报告澄清 layered_kinematic 与 elastic2d 使用的是不同层级的速度模型。

- empirical relation：`Rayleigh equivalent velocity ≈ 0.9 * Vs`
- layered Rayleigh equivalent velocity：`[120.0, 180.0, 260.0, 350.0]` m/s
- implied Vs from Rayleigh：`[133.33333333333334, 200.0, 288.88888888888886, 388.88888888888886]` m/s
- elastic2d Vp：`500.0` m/s
- elastic2d Vs：`250.0` m/s
- elastic2d rho：`1800.0` kg/m3
- elastic2d 0.9Vs equivalent：`225.0` m/s
- consistency：`consistent`
- elastic Vs / implied Vs ratio：`1.023`
- Rayleigh pick failure may reflect parameter mismatch：`False`

## 结论

当前 elastic2d 参数不能自动代表主流程的 layered Rayleigh equivalent velocity。
如果二者不匹配，Rayleigh-like 拾取失败可能同时包含数值格式问题和参数物理层级不一致问题。
下一步应从 Rayleigh equivalent velocity 反推 Vs，并用实测或文献关系约束 Vp/Vs/rho。