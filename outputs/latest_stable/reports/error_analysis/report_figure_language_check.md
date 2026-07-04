# 图件语言检查报告

本报告不使用 OCR，而是检查 latest_stable figure manifest 的 `language=zh` 标记和绘图 case label 映射。
DAS、Rayleigh、Vp、Vs、CFL、PML、RMS、gauge length 等标准缩写允许保留。

- 检查图件总数：`23`
- 英文图或需中文化图数量：`0`
- 状态：`pass`
- 允许缩写：`['DAS', 'Rayleigh', 'Vp', 'Vs', 'CFL', 'PML', 'RMS', 'x-y-depth', 'gauge length']`

## 需要中文化清单

- `无`

## case label 中文化审计

- 检查图件数量：`23`
- 英文 case label 数量：`0`
- 状态：`pass`
- 允许保留缩写：`['CFL', 'DAS', 'PML', 'RMS', 'Rayleigh', 'Vp', 'Vs', 'gauge length', 'x', 'y', 'z']`

### 已登记中文映射

- `approximate` -> 近似自由面
- `collocated` -> 共点网格
- `collocated_horizontal` -> 共点网格-水平力源
- `collocated_vertical` -> 共点网格-垂向力源
- `explosive` -> 爆炸源近似
- `horizontal_force` -> 水平力源
- `medium` -> 中等
- `sponge_medium` -> 中等海绵边界
- `sponge_strong` -> 强海绵边界
- `sponge_weak` -> 弱海绵边界
- `staggered` -> 错格网格
- `staggered_horizontal` -> 错格网格-水平力源
- `staggered_traction_variant` -> 错格网格-自由面变体
- `staggered_vertical` -> 错格网格-垂向力源
- `stress_zero` -> 应力置零
- `stress_zero_variant` -> 应力置零自由面
- `strong` -> 强
- `traction_free` -> 近似零牵引
- `vertical_force` -> 垂向力源
- `weak` -> 弱

### 仍需处理的英文 case label

- `无`