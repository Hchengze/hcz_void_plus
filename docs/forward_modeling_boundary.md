# 正演能力边界

本文件用于约束报告、README、summary 和代码注释的专业表达，避免把当前能力写得过强。

## 当前主流程

1. 当前主流程仍是 `DAS-like response approximation`。
2. 当前主流程仍是 `kinematic approximation`。
3. 当前 active forward engine 是 `layered_kinematic`。
4. `layered_kinematic` 是 `straight-ray kinematic approximation`，通过路径采样积分 `integral ds / v(x,y,z)` 计算走时。
5. 当前三维几何是 `source_xyz / receiver_xyz / candidate_xyz` 的运动学几何。
6. 当前异常体是 `equivalent scatter representation`，不是真实边界散射。

## 不能宣称的内容

1. 不能把当前结果写成工程确诊。
2. 不能把 straight-ray layered kinematic approximation 写成真实全波场。
3. 不能把 2D acoustic FDTD prototype 写成 Rayleigh 波正演。
4. 不能把当前 DAS-like 点接收近似写成真实 DAS 仪器响应。
5. 不能把 full 3D elastic 写成下一轮默认主流程。

## wave-equation prototype 的角色

- `acoustic2d_prototype` 只验证网格、震源、接收、吸收边界、CFL 和快照输出等波动方程基础设施。
- Rayleigh 波、自由表面、空洞散射和 DAS-like gauge strain 的核心验证应进入 `elastic2d`。
- 所有 wave-equation prototype 先作为 validation，不替代当前 `layered_kinematic` 主定位流程。

## 三维道路 DAS-like 风险

真实三维道路 DAS-like 场景中，正演真实性、速度模型不确定性、观测几何、DAS gauge response 与 y-depth 耦合是迁移能力的核心风险。单侧线状 DAS-like 几何下，y 和 depth 的可分辨性天然有限，应优先输出三维高分候选体和不确定性区域，而不是强行输出单点。
