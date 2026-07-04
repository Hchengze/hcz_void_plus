# 2D Elastic 正演设计

`elastic2d_prototype` 是 Stage 5C 引入的 Rayleigh/free-surface/void scattering 局部物理验证起点。本文件同时记录设计约束和当前最小实现边界：它不是工业级 elastic solver，也不替代三维主定位流程。

## 方程

- 采用 2D velocity-stress elastic wave equation。
- 状态量包括速度分量和应力分量。
- 介质参数包括 `Vp`、`Vs` 和 `rho`。

## 自由表面与边界

- 路表 `z=0` 应实现 free surface。
- 左、右、底部边界应使用 PML 或 sponge absorbing boundary。
- 边界实现必须先通过均匀半空间传播测试和能量稳定性测试。

## 震源与接收

- 震源优先使用 vertical force / hammer-like source。
- 接收量包括 surface displacement、surface velocity 和后续 DAS-like strain。
- DAS-like 响应应沿 receiver tangent 做 gauge-length strain，而不是简单点接收。

## 异常体表达

- void 可以用低 `Vs`、低密度、空洞边界或 trench/pipe disturbance 近似。
- 初期只做小域局部验证，不把异常体结果写成工程确诊。

## 输出与验证

- 输出 wavefield snapshots、shot gather、DAS-like strain gather。
- 验证步骤包括均匀半空间 Rayleigh 传播速度、分层模型、空洞散射和绕射曲线对比。
- 与当前 `layered_kinematic` 的关系是物理验证和校正，不是直接替代全部三维扫描主流程。

## 当前边界

当前 Stage 5C 已实现最小 collocated-grid velocity-stress prototype，状态量包括 `vx / vz / sxx / szz / sxz`，介质参数包括 `Vp / Vs / rho / lambda / mu`。该原型支持 Ricker vertical force、surface receiver line、sponge boundary、近似 free surface、surface gather、wavefield snapshots、CFL 检查和低速 void-like 扰动。

该实现仅用于科研验证：

- collocated-grid 数值精度有限；
- 顶部 free surface 是近似处理；
- sponge boundary 不是严格 PML；
- void-like anomaly 是低速/低密度扰动，不是真实空洞边界条件；
- DAS-like gauge strain 是由 surface velocity 的有限差分近似，不是真实仪器响应。

下一步应优先加固数值稳定性、自由表面处理、PML、Rayleigh 速度验证和 2.5D 多剖面验证，而不是直接宣称 full 3D elastic 能力。
