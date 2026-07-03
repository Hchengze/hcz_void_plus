# hcz_void_plus

城市道路既有通信光纤 DAS 空洞探测科研级算法原型平台。

项目面向道路地下空洞、脱空、松散区、管沟、管线周边扰动、弱夹层和破碎带等浅层异常体。典型几何为单侧 DAS-like 接收：光纤沿道路方向布设，近似位于 `y = 0`；震源线位于道路另一侧或道路边缘，近似位于 `y = W`；异常体位于道路下方 `(x0, y0, h)`。

## 当前 Stage 2 已实现

- `main.py` 统一 argparse 参数中心。
- DAS-like point receiver approximation。
- uniform effective Rayleigh velocity。
- 运动学直达波 + 等效散射/绕射波多炮正演。
- 中文几何图、中文炮集图、中文报告。
- 运动学伪波场快照和传播示意 GIF。
- 直达波到时预测、直达波 mute、局部能量属性。
- 基础 x-y-h 多炮扫描定位。
- `score_volume` 输出和扫描切片图。

## 如何运行

当前本机环境可使用：

```bash
D:\HczApp\Anaconda\envs\mywork\python.exe -m pytest
D:\HczApp\Anaconda\envs\mywork\python.exe main.py --task debug
D:\HczApp\Anaconda\envs\mywork\python.exe main.py --task forward --max-shot-gather-figures 2 --wavefield-snapshot-count 8
D:\HczApp\Anaconda\envs\mywork\python.exe main.py --task full_pipeline --max-shot-gather-figures 2 --wavefield-snapshot-count 8
```

如果系统 PATH 中有 Python，也可以把前缀替换为 `python`。

## 输出目录

每次运行会创建：

```text
outputs/<run_name>_<timestamp>/
├── arrays/
├── figures/
├── snapshots/
├── animations/
├── reports/
├── logs/
└── metadata/
```

文件名前缀：

- `arr_`：数组，例如 `arr_synthetic_data.npy`、`arr_score_volume.npy`
- `fig_`：普通静态图，例如 `fig_geometry.png`
- `snap_`：运动学伪波场快照
- `anim_`：传播示意 GIF
- `report_`：Markdown 报告
- `meta_`：元数据
- `log_`：日志
- `params_`：参数快照

## 控制输出数量

```bash
--max-shot-gather-figures 2
--wavefield-snapshot-count 8
--save-wavefield-snapshots false
--save-wavefield-animation false
```

默认只输出少量炮集图和有限数量伪波场帧，不会保存所有炮或所有时间帧。

## 基础扫描定位

Stage 2 的扫描方法是 `diffraction_energy_stack`：

1. 构建候选异常体位置 `x-y-h` 网格；
2. 计算 `source -> candidate -> receiver` 理论散射走时；
3. 在 DAS-like 数据中沿对应走时时间窗提取局部能量；
4. 对所有 shot 和 channel 求平均形成 `score_volume`；
5. 最高得分位置作为 `best_location`。

`score_volume` 保存于：

```text
arrays/arr_score_volume.npy
arrays/arr_scan_x_grid.npy
arrays/arr_scan_y_grid.npy
arrays/arr_scan_depth_grid.npy
```

## 当前近似和限制

- 当前结果必须称为 `DAS-like response approximation`。
- 当前正演、伪波场和扫描都属于 `kinematic approximation`。
- 伪波场快照是 `kinematic pseudo-wavefield snapshot`，不是弹性波方程数值模拟。
- GIF 是传播示意动图，不是真实全波场模拟。
- 当前速度模型为 `uniform effective Rayleigh velocity`。
- 当前 DAS-like 响应是点式接收近似，尚未实现真实 gauge length 响应。
- `best_location` 是运动学局部能量聚焦结果，不能作为工程确诊结论。
- 单侧 DAS-like 几何下，横向 y 和埋深 h 可能耦合。

后续阶段再做完整置信度、鲁棒性参数扫描、DAS gauge length、分层速度和局部全波场验证。
