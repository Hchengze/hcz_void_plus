# DAS-like Approximation

当前结果必须称为 `DAS-like response approximation`。

## 当前实现

Stage 1 只实现 `point_receiver approximation`。每个光纤通道被近似为一个点式接收器，数据形状为：

```text
shot × time × channel
```

## 明确限制

当前不是完整 DAS 仪器模拟。尚未完整考虑：

- gauge length 内的空间差分或积分响应；
- 光纤方向敏感性；
- 光缆-道路耦合条件；
- 解调过程；
- 仪器响应；
- 应变或应变率的严格转换。

`gauge_length_m` 已经进入统一参数对象和 metadata，但在 point receiver 模式下不参与波形计算。
