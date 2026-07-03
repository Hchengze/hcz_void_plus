# Reference Backed Algorithm Plan

## 已吸收方向

1. Rayleigh diffraction 数据增强：
   - bandpass；
   - trace normalization；
   - AGC；
   - envelope；
   - 简化 f-k 速度扇区滤波接口。

2. 三维运动学定位：
   - 任意 `source_xyz` / `receiver_xyz` 点集；
   - x-y-depth 三维候选扫描；
   - 三维高分候选体表达。

3. 多属性评分：
   - energy_score；
   - normalized_energy_score；
   - matched_wavelet_score；
   - semblance_score；
   - frequency_shift_score 预留。

## 后续计划

- 进一步审计 reference PDF 的题名、公式和实验设置；
- 在 `literature_reproduction` 中做小型复现实验；
- 增强 f-k filter，使其更接近文献中的 Rayleigh-wave diffraction filtering；
- 增加多异常体和任意 polyline DAS 几何；
- 使用局部全波场验证检查 kinematic scan 的适用范围。

