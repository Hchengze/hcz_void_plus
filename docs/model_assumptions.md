# Model Assumptions

## 研究对象

城市道路浅层异常体：地下空洞、脱空、松散区、管沟、管线周边扰动、弱夹层和破碎带。

## 坐标

- `x`：沿道路和光纤方向。
- `y`：横穿道路方向。
- `z / h`：深度方向，向下为正。

## Stage 3 模型

- 正演：运动学直达波 + 运动学等效散射/绕射波。
- 子波：Ricker 子波。
- 速度：`uniform effective Rayleigh velocity`。
- 地表响应：基于 Rayleigh 波走时控制的 `kinematic_surface_response_snapshot`。
- 扫描：基于理论散射走时的局部能量聚焦。
- 深度敏感性：使用 `exp(-h / penetration_depth)` 作为 Rayleigh 波浅层敏感性的简化近似，其中 `penetration_depth = rayleigh_penetration_factor * wavelength`。
- 基础置信度：基于 score volume 形态、多炮贡献一致性和 y-depth 高分区跨度的规则型诊断。
- Stage 3B：raw score 与 depth-weighted score 分离，并显式诊断深度边界、浅部偏置和 raw/weighted 分歧。

## 三维坐标与当前观测系统

当前代码中的 source、receiver 和 candidate 都使用三维坐标计算走时，因此 depth 不是绘图标签，而是路径距离中的 z 坐标。但当前观测系统仍然是单光纤线 + 单震源线，尚未支持任意三维 source/receiver polyline 或多异常体三维形状。

## 限制

当前不是完整三维弹性波全波场模拟。地表响应示意图和 GIF 不是真实弹性波方程数值模拟。空洞、脱空和松散区不会简单等价为地下各向同性点源；多个散射点只是快速运动学近似，用于构造绕射走时和定位属性。Rayleigh 深度敏感性权重不是严格模态深度核。

Stage 3 的 confidence flag 不是概率置信度，也不是工程确诊；它只帮助用户判断当前候选定位结果是否值得进一步人工检查。
# Stage 5A 当前模型假设提示

本文件若包含早期 uniform-only 表述，应理解为历史阶段说明。当前 Stage 5A 已支持 `uniform / layered / lateral_gradient / localized_low_velocity_zone / layered_with_anomaly_perturbation`。

分层/非均匀速度通过 straight-ray kinematic approximation 进入正演和扫描：

```text
travel_time = integral(ds / v(x, y, z))
```

该近似不做 Snell 射线弯曲，不是 3D elastic wavefield，也不是速度反演。
