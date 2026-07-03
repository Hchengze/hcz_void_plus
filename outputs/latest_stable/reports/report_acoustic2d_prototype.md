# acoustic2d prototype 验证报告

`acoustic2d_prototype` 是二维标量 acoustic FDTD 最小原型。它只用于验证波动方程基础设施，不能代表 Rayleigh 波、自由表面或空洞弹性散射正演。

## 输出

- shot gather shape：`(1980, 48)`。
- wavefield snapshot shape：`(6, 101, 201)`。
- snapshot count：`6`。
- CFL stable：`True`。
- CFL number：`0.5`。
- max abs amplitude：`14.45`。
- energy：`0.005463`。

## 能验证什么

- 二维网格和分层 acoustic velocity 的组织方式。
- Ricker 震源、接收线和 shot gather 输出。
- sponge absorbing boundary 与 CFL 稳定性检查。
- wavefield snapshots 的保存和可视化链路。

## 不能验证什么

- 不能验证 Rayleigh 波。
- 不能验证自由表面条件。
- 不能验证 void/free-surface/elastic scattering。
- 不能替代 `layered_kinematic` 主流程，也不能替代下一步 `elastic2d`。