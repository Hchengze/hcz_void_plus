# DAS-like Approximation

当前结果必须称为 `DAS-like response approximation`。

Stage 2 仍然只实现 `point_receiver approximation`：每个光纤通道被近似为一个点式接收器，输出数据形状为：

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
