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

## 稳定定位策略

1. 用分层/非均匀 velocity model 计算直达波与绕射走时。
2. 对数据执行推荐预处理。
3. 使用 `multi_attribute_unweighted` score 做主扫描。
4. 使用 depth-weighted score、velocity ablation 和 model mismatch 做风险诊断。
5. 输出 high-score region、connected components、recommended_location_type 和 uncertainty interval。

当前结果是科研候选区，不是工程确诊。
