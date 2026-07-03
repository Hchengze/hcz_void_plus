# Three Dimensional Geometry Plan

## 当前状态

当前代码已经使用三维坐标数组：

- `source_xyz`：shape = `n_shot × 3`
- `receiver_xyz`：shape = `n_channel × 3`
- `candidate_xyz`：shape = `3`

走时计算使用三维欧氏距离，因此异常体深度 `h` 已经作为 z 坐标进入 `source -> candidate -> receiver` 路径长度。当前观测系统仍然是单光纤线 + 单震源线：

- DAS-like 光纤测线近似位于 `y = 0`
- 震源测线近似位于 `y = W`
- 道路区域为 `0 <= y <= W`

## Stage 3B 诊断意义

单侧线状观测系统对 x 方向约束通常较稳定，但 y 与 depth 可能耦合。Rayleigh depth weighting 是浅层敏感性的简化先验，可能把 weighted_best 推向浅部边界。因此 Stage 3B 同时输出 raw_best 和 weighted_best，并增加边界、宽 y、高分带和浅部偏置 warning。

## 后续三维化路线

后续阶段计划支持：

1. 任意 `source_xyz` 点集，而不是单条规则震源线；
2. 任意 `receiver_xyz` polyline，而不是单条规则光纤线；
3. 多条光纤或道路多边界布设；
4. 多异常体候选与三维形状参数；
5. 候选体从单点扩展为椭球、盒体、管线扰动带或离散散射体集合；
6. 对 y-depth 耦合做更系统的不确定性分析；
7. 使用局部全波场验证检查运动学扫描结果。

当前项目仍是科研级算法原型，不是工程确诊系统，不实现 elastic2d、elastic3d、FEM、SEM、BEM 或 FWI。
