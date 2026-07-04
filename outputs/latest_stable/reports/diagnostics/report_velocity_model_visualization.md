# 当前速度模型可视化报告

本报告回答当前主流程到底是不是 layered / heterogeneous velocity，而不是只存在源码文件。

- active velocity_model_type：`layered`
- layer depths m：`[0.3, 1.0, 3.0, 8.0]`
- layer velocities m/s：`[120.0, 180.0, 260.0, 350.0]`
- sampling path velocity min/max/mean：`120.0` / `260.0` / `226.0` m/s
- uniform vs active direct RMS difference：`215.7` ms
- uniform vs active direct max abs difference：`500.2` ms

## 解释

- 当前 layered_kinematic 使用等效 Rayleigh 速度模型和 straight-ray 路径采样积分。
- 该模型不是完整 Vp/Vs/rho 弹性模型，也不是速度反演结果。
- elastic2d_prototype 的 Vp/Vs/rho 是独立 validation 参数，与本报告中的 Rayleigh equivalent velocity 不属于同一层级。
- 下一步若要进入真实数据，应优先做实测速度标定或速度反演约束。