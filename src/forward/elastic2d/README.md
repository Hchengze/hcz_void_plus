# elastic2d planned forward

本目录是 Stage 5C 建立的 2D elastic velocity-stress 科研验证原型区。当前实现是最小 collocated-grid prototype，不是完整工业级 elastic solver，也不会把 acoustic2d prototype 误写成 Rayleigh 波正演。

后续实现应包含：

1. 2D velocity-stress elastic wave equation；
2. `Vp / Vs / rho` 介质参数；
3. `z=0` free surface；
4. PML 或 sponge absorbing boundary；
5. hammer-like vertical force source；
6. surface displacement / velocity receiver；
7. receiver tangent 上的 gauge-length DAS-like strain；
8. void / low Vs / low density / trench 等异常体表达；
9. wavefield snapshots、shot gather 和 DAS-like strain gather；
10. Rayleigh 传播速度、分层模型和空洞散射验证。

当前主定位 forward 仍是 `layered_kinematic`，`elastic2d_prototype` 只作为 Rayleigh-like/free-surface/void-like scattering 的局部物理验证起点。后续需要继续加固自由表面、PML、数值色散和 2.5D 多剖面验证。
