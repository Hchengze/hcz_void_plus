# 当前稳定三维算法概览

## 几何与主问题

- 项目最终场景仍是三维道路 DAS-like 空洞探测，核心坐标为 `source_xyz`、`receiver_xyz`、`candidate_xyz`。
- 当前稳定输出必须保留 x-y-depth high-score region、connected components、推荐候选区和不确定性区间。
- 2D elastic 结果只用于局部物理验证，不能直接替代三维 x-y-depth 定位结论。

## 速度模型

Stage 5A 起，稳定主线默认使用 `layered` 等效 Rayleigh 速度模型。

- `uniform`：基线对比和诊断，不是当前默认主流程。
- `layered`：当前 active velocity model，通过路径采样积分进入 direct、scatter 和 scan travel-time。
- `lateral_gradient`、`localized_low_velocity_zone`、`layered_with_anomaly_perturbation`：研发区用于敏感性检查。

`layered_kinematic` 中的速度是等效 Rayleigh 速度；`elastic2d_prototype` 与 staggered benchmark 使用 Vp/Vs/rho 弹性参数。二者属于不同物理层级，不能直接当作同一速度模型。

## 正演主线

- F0 `kinematic_baseline`：均匀速度运动学快速基线。
- F1 `layered_kinematic`：当前 active forward engine，采用 straight-ray kinematic approximation。
- F2 `acoustic2d_prototype`：声学波动方程基础设施验证，不代表 Rayleigh 波正演。
- F3 `elastic2d_prototype`：Rayleigh/free-surface/void scattering 的局部科研验证起点。
- Stage 5F 新增 collocated / staggered elastic2d Rayleigh-like benchmark，但它仍是 validation forward，不替代主定位 forward。

## 稳定输出准入

- 稳定定位策略仍以 `multi_attribute_unweighted` score、x-y-depth high-score region 和 uncertainty interval 共同表达候选区。
- `latest_stable` 只保存当前精选成果，不是历史图件仓库。
- 进入 `latest_stable` 的图件必须通过文件级自检、科学结论自检、空图质量检查、重复检查和图件语言检查。
- 空图、重复图、旧阶段主结论图和明显英文图不得进入当前精选目录。
- 若 Rayleigh-like benchmark 未通过，报告和 summary 不得宣称 Rayleigh 正演成功。
- 若 DAS-like gauge strain 很弱或不可解释，默认定位不得使用 gauge strain。

## Stage 5F 边界

- active forward engine：`layered_kinematic`。
- active velocity model：`layered`。
- validation forward：`acoustic2d_prototype`、`elastic2d_prototype`、`staggered_elastic2d_benchmark`。
- ready_for_2p5d：默认 `False`，除非 Rayleigh benchmark、DAS gauge response、void residual 和 latest_stable 一致性全部通过。

当前结果仍是科研候选区，不是工程确诊。
