# elastic2d 数值格式加固计划

## 当前 collocated-grid 限制

当前 `elastic2d_prototype` 使用最小 collocated-grid velocity-stress 格式，变量 `vx / vz / sxx / szz / sxz` 放在同一网格点。它便于审计和快速验证，但存在几个明确限制：

1. 自由表面只通过顶部应力置零近似处理，不是严格 traction-free 边界。
2. sponge boundary 只是指数衰减，不是 PML。
3. collocated-grid 对交错应力-速度耦合的数值色散和伪模式控制较弱。
4. Rayleigh-like surface event 可能被体波、边界反射、弱表面事件或拾取窗口误导。
5. 该原型不能作为工业级 elastic solver，也不能作为真实 DAS 仪器响应。

## staggered-grid 的优势

staggered-grid velocity-stress FDTD 将速度和应力放在交错位置：

- `vx` 位于 x 方向半格点；
- `vz` 位于 z 方向半格点；
- `sxx / szz` 位于单元中心；
- `sxz` 位于交错角点。

这种布局更适合弹性波速度-应力耦合，可降低数值伪模式，并为更严格 free-surface 和 PML 打基础。

## 更严格自由表面路线

短期应从当前 `approximate` 和 `stress_zero_variant` 对比开始，判断 Rayleigh-like 检测失败是否对表面应力处理敏感。下一步应实现：

1. staggered-grid traction-free 边界；
2. 对 `szz=0`、`sxz=0` 的一致差分处理；
3. 表面速度点与应力点的正确插值；
4. 与均匀半空间 Rayleigh 速度范围的 sanity check。

## PML 与 sponge

当前 sponge 只做幅值衰减，可能影响近地表波或产生残余反射。PML 应作为下一步方向，但本轮不实现 PML。本轮只做 `weak / medium / strong` sponge 对比，判断边界反射是否主导拾取失败。

## 本轮最小升级

本轮实现：

- collocated-grid 参数敏感性对比；
- `free_surface_mode` 对照；
- `sponge_strength_mode` 对照；
- `receiver_depth_index` 对照；
- staggered-grid 数据结构与 CFL/layout 检查；
- scientific figure self-check。

本轮不实现成熟 staggered-grid 求解器，不进入 2.5D 或 3D elastic。

## 下一轮条件

只有当 Rayleigh-like 检测在 elastic2d 中稳定通过，且 DAS-like gauge strain 有非零且可解释的响应后，才建议进入 2.5D 多剖面验证。
