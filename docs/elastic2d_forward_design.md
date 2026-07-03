# 2D Elastic 正演设计

`elastic2d` 是 Stage 5B 后下一阶段 Rayleigh/free-surface/void scattering 的核心局部全波场方向。本文件是设计约束，不代表当前已经完成工业级 elastic solver。

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

当前 Stage 5B 没有实现完整 elastic2d solver。`src/forward/elastic2d/` 只提供设计文档和占位入口，避免后续开发继续绕回单纯 kinematic warning。
