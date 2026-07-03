# DAS-like Approximation

当前结果必须称为 `DAS-like response approximation`。

Stage 3 仍然只实现 `point_receiver approximation`：每个光纤通道被近似为一个点式接收器，输出数据形状为：

```text
shot × time × channel
```

## 尚未实现

- gauge length 内的真实空间响应；
- 光纤方向敏感性；
- 光缆-道路耦合条件；
- 解调过程；
- 仪器响应；
- 严格应变或应变率转换。

`gauge_length_m` 已进入统一参数对象和 metadata，但在 point receiver 模式下不参与波形计算。

## 与 Rayleigh 地表响应图的关系

运动学地表响应示意图只显示 x-y 表面的相对响应趋势，不是 DAS 仪器响应，也不是光纤应变率的严格模拟。真实 DAS 响应还需要考虑 gauge length、轴向应变、耦合条件和解调过程。

基础置信度诊断同样建立在该 DAS-like 点式接收近似之上，因此只能评价当前运动学数据和扫描属性的内部稳定性，不能替代真实 DAS 数据质量评价或工程诊断。

Stage 3B 中 raw_best 与 weighted_best 的差异主要反映运动学扫描属性和 Rayleigh 深度先验之间的张力，并不代表 DAS 仪器响应本身已经被精确建模。真实 DAS gauge length、轴向应变和耦合条件仍待后续阶段实现。
# 历史阶段提示

本文件包含 Stage 3/Stage 4 的 DAS-like 近似说明，不代表当前完整主线。当前主线请以 `README.md`、`docs/current_status.md`、`docs/current_algorithm_boundary.md` 和 `code/current_3d_algorithm/` 为准。
