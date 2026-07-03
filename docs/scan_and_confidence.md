# Scan And Confidence

Stage 2 只实现基础扫描定位，不实现完整置信度体系。

## 扫描方法

当前方法为 `diffraction_energy_stack`：

1. 构建候选异常体位置 `x-y-h` 网格；
2. 计算 `source -> candidate -> receiver` 理论散射走时；
3. 在 DAS-like 数据中沿对应走时时间窗提取局部能量；
4. 对所有炮和通道求平均，形成 `score_volume`；
5. 最高得分点作为 `best_location`。

## score volume

`score_volume` 是每一个候选异常体位置的扫描得分体，shape 为：

```text
n_x × n_y × n_depth
```

它保存于 `arrays/arr_score_volume.npy`，对应网格保存于：

- `arrays/arr_scan_x_grid.npy`
- `arrays/arr_scan_y_grid.npy`
- `arrays/arr_scan_depth_grid.npy`

## 风险提示

单侧 DAS-like 几何下，横向位置 y 和埋深 h 可能耦合。Stage 2 的 best_location 是运动学局部能量聚焦结果，不能作为工程确诊结论。

完整置信度体系、鲁棒性扫描、peak sharpness、score contrast 和 multi-shot consistency 留到后续阶段。
