# 当前稳定三维算法概览

## 几何

- 三维坐标：`x` 沿道路，`y` 横穿道路，`z/depth` 向下为正。
- 默认观测系统仍是单光纤线 + 单震源线，但研发区已经支持 receiver polyline 与 source grid/csv。
- 当前推荐把结果表达为三维候选体和不确定性区间。

## 速度模型

Stage 5A 起，稳定主线默认使用 `layered` 等效 Rayleigh 速度模型：

- `uniform`：基线对比；
- `layered`：路面/基层/土体等分层等效速度；
- `lateral_gradient`：道路横向或沿线速度缓变；
- `localized_low_velocity_zone`：回填区或局部低速扰动；
- `layered_with_anomaly_perturbation`：分层背景叠加异常附近低速扰动。

所有速度模型仍采用 straight-ray kinematic approximation，不做射线弯曲或弹性波模拟。

## 正演主线

Stage 5C 后，稳定算法区明确采用以下 forward 路线；Stage 5D 继续要求速度模型调用链和输出图件都可审计；Stage 5E 进一步要求科学图件自检、速度物理桥接和 elastic2d 数值格式加固：

- F0 `kinematic_baseline`：保留为快速均匀速度运动学基线。
- F1 `layered_kinematic`：当前 active forward engine，通过 `velocity_model` 路径采样积分计算直达和散射走时。
- F2 `acoustic2d_prototype`：二维标量 acoustic FDTD validation，只验证网格、震源、接收、sponge boundary、CFL 和快照输出。
- F3 `elastic2d_prototype`：Rayleigh/free-surface/void scattering 局部物理验证起点。
- F4-F6：面向三维几何的多剖面 elastic、小域 3D elastic 和外部 solver adapters。

`acoustic2d_prototype` 不能代表 Rayleigh 波正演；当前主定位仍使用 `layered_kinematic`，结果仍是科研候选区。

## 稳定定位策略

1. 用分层/非均匀 velocity model 计算直达波与绕射走时。
2. 对数据执行推荐预处理。
3. 使用 `multi_attribute_unweighted` score 做主扫描。
4. 使用 depth-weighted score、velocity ablation 和 model mismatch 做风险诊断。
5. 输出 high-score region、connected components、recommended_location_type 和 uncertainty interval。

当前结果是科研候选区，不是工程确诊。

## Stage 5D/5E 稳定输出准入

- `layered_kinematic` 仍是 active forward engine。
- `direct_wave`、`scatter_kinematic` 和 `scan travel-time` 必须使用 velocity_model travel-time 接口。
- `uniform` 只作为 baseline/diagnostic，不作为默认主线。
- `latest_stable` 只保留精选成果，图件进入前必须通过 figure self-check。
- `elastic2d_prototype` 输出 Rayleigh-like pick、void residual、DAS-like gauge response 和 elastic-vs-kinematic 能量分解，但仍只是 validation forward。
- Stage 5E 后，进入 `latest_stable` 的图件还必须通过 scientific figure self-check；如果 Rayleigh-like 检测未通过，报告和 summary 不得宣称 Rayleigh 正演成功。
- `layered_kinematic` 使用的是等效 Rayleigh velocity；`elastic2d_prototype` 使用 Vp/Vs/rho，二者必须通过经验关系或实测标定桥接，不能当作同一速度模型。
- 当前 staggered-grid 只沉淀布局、CFL 和更新公式计划，尚未作为成熟求解器接入。
- 未通过 Rayleigh/free-surface 基础验证前，不建议进入 2.5D 或局部 3D elastic。
