# 正演引擎消融报告

本报告比较 `kinematic_baseline`、`layered_kinematic` 与 `acoustic2d_prototype` 的阶段角色。
`acoustic2d_prototype` 只验证波动方程数值框架，不参与 DAS-like 主定位，也不能代表 Rayleigh 波正演。

| engine | stage | velocity/model | data/snapshot shape | RMS or max amplitude | role |
|---|---|---|---|---:|---|
| kinematic_baseline | F0 | uniform | (9, 801, 121) | 0.02178 | F0 快速基线 |
| layered_kinematic | F1 | layered | (9, 801, 121) | 0.01885 | F1 当前主线 |
| acoustic2d_prototype | F2 | scalar acoustic | (1980, 48) / (6, 101, 201) | 14.45 | F2 validation prototype |

## F1 相对 F0 的差异

- synthetic RMS difference：`0.02875`。
- synthetic relative difference：`1.32`。
- travel-time residual mean：`53.89` ms。
- travel-time residual RMS：`57.08` ms。
- travel-time residual max abs：`102.4` ms。

## acoustic2d prototype 边界

- CFL stable：`True`。
- CFL number：`0.5`。
- acoustic2d 只有标量声学压力场，没有剪切波和自由表面 Rayleigh 模式。
- acoustic2d 可以验证网格、震源、接收、absorbing boundary、CFL 和快照输出。
- acoustic2d 不能验证 Rayleigh/free-surface/void scattering；下一步必须进入 elastic2d。

## 当前结论

- active forward engine：`layered_kinematic`。
- available forward engines：`kinematic_baseline, layered_kinematic, acoustic2d_prototype`。
- next required forward：`elastic2d`。
- 当前结果仍是科研候选区，不是工程确诊。