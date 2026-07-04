# elastic2d void / low Vs scattering 报告

本报告比较背景模型和低 Vp/低 Vs/低密度 void-like 扰动模型的 surface gather。

- residual_energy：`1.705e-17`。
- relative_residual_energy：`1.705e-05`。
- void_residual_visible：`True`。
- scatter center：x=`4.96` m, z=`2.25` m。
- parameter sensitivity best case：`vertical_force_r1.5_vs0.2`。
- parameter sensitivity best residual energy：`1.1075624099111773e-16`。

## 解释

- 低速扰动可产生可见 residual，但它不是严格空腔边界条件。
- residual envelope 会与局部 kinematic diffraction curve 做叠加，检查运动学走时在哪些位置仍有解释力。
- elastic2d 会出现振幅、频率、尾波和多路径等运动学模型没有的效应。
- 下一步需要更严格 free surface、PML 和 staggered-grid 精度硬化。