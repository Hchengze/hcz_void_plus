# Model Assumptions

## 研究对象

城市道路浅层异常体：地下空洞、脱空、松散区、管沟、管线周边扰动、弱夹层和破碎带。

## 坐标

- `x`：沿道路和光纤方向。
- `y`：横穿道路方向。
- `z / h`：深度方向，向下为正。

## Stage 2 模型

- 正演：运动学直达波 + 运动学等效散射/绕射波。
- 子波：Ricker 子波。
- 速度：`uniform effective Rayleigh velocity`。
- 地表响应：基于 Rayleigh 波走时控制的 `kinematic_surface_response_snapshot`。
- 扫描：基于理论散射走时的局部能量聚焦。
- 深度敏感性：使用 `exp(-h / penetration_depth)` 作为 Rayleigh 波浅层敏感性的简化近似，其中 `penetration_depth = rayleigh_penetration_factor * wavelength`。

## 限制

当前不是完整三维弹性波全波场模拟。地表响应示意图和 GIF 不是真实弹性波方程数值模拟。空洞、脱空和松散区不会简单等价为地下各向同性点源；多个散射点只是快速运动学近似，用于构造绕射走时和定位属性。Rayleigh 深度敏感性权重不是严格模态深度核。
