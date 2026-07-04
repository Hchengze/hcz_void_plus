# elastic2d 与 layered_kinematic 对照报告

本报告把 elastic2d residual gather 与局部 kinematic diffraction curve 叠加，检查运动学走时对 elastic residual 的解释能力。

- curve_energy_ratio：`1.198e-07`。
- residual_energy_near_kinematic_curve_ratio：`1.1981878201949605e-07`。
- residual_energy_off_curve_ratio：`0.999999880181218`。
- best_time_shift_ms：`10.0`。
- kinematic_curve_explained_fraction：`0.00022196748680872161`。
- elastic_extra_event_fraction：`0.9997780325131913`。
- main conclusion：layered/局部 kinematic 曲线只能解释 elastic residual 的一部分能量；曲线外 residual 代表振幅、尾波、多路径、边界和弹性模式等运动学模型没有的效应。

## 结论边界

- layered_kinematic 曲线可解释部分主要到时，但不能解释完整振幅、频率、尾波和多路径。
- 低解释比例可能来自 Rayleigh-like 拾取未通过、body wave / boundary reflection 占主导，或 collocated-grid/free-surface 原型仍不稳定。
- 这说明当前 kinematic localization 不能直接用 elastic residual 的全波形能量来评价迁移能力。
- matched wavelet、frequency shift、semblance 等定位属性暂不应基于该 elastic residual 强行调参。
- x-y-h 三维定位仍可继续使用 kinematic 主线做快速候选区扫描。
- 深度、横向 y、振幅和频率解释必须等 elastic validation 更成熟后再推进。
- 当前结果是科研候选区，不是工程确诊。