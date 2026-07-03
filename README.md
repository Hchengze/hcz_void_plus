# hcz_void_plus

城市道路既有通信光纤 DAS 空洞探测科研级算法原型平台。

项目面向道路地下空洞、脱空、松散区、管沟、管线周边扰动、弱夹层和破碎带等浅层异常体。典型几何为单侧 DAS-like 接收：光纤沿道路方向布设，近似位于 `y = 0`；震源线位于道路另一侧或道路边缘，近似位于 `y = W`；异常体位于道路下方 `(x0, y0, h)`。

## 当前 Stage 3 已实现

- `main.py` 统一 argparse 参数中心。
- DAS-like point receiver approximation。
- uniform effective Rayleigh velocity。
- 运动学直达波 + 等效散射/绕射波多炮正演。
- 中文几何图、中文炮集图、中文报告。
- 运动学地表响应示意图和传播示意 GIF。
- Rayleigh 波简化深度敏感性权重。
- 直达波到时预测、直达波 mute、局部能量属性。
- 基础 x-y-h 多炮扫描定位。
- `score_volume` 输出和扫描切片图。
- 等效散射路径剖面图、Rayleigh 深度敏感性图、绕射走时曲线自检图。
- 基础置信度诊断：peak sharpness、score contrast、multi-shot consistency、y-depth coupling warning 和 high/medium/low 规则型标志。
- Stage 3B 扫描稳健化：raw score 与 depth-weighted score 分离，显式输出 raw_best、weighted_best 和二者差异。
- Stage 3B 新增 warning：深度边界、宽 y 高分区、raw/weighted 分歧、浅部偏置。
- 直达波 mute 默认改为 `taper`，保留 `hard/subtract/none`。
- 新增 `normalized_energy_stack` 作为可选扫描得分方法。
- `outputs/latest_stable/` 精选稳定成果导出，便于每轮人工快速检查。

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

`full_pipeline` 默认还会刷新固定目录：

```text
outputs/latest_stable/
├── figures/
├── animations/
├── reports/
├── metadata/
└── summary.md
```

`latest_stable` 只保留最值得人工检查的精选图件、报告和 metadata；时间戳运行目录仍保留完整本地结果。大型数组、批量快照和中间产物默认不提交到 Git。

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
4. 对所有 shot 和 channel 求平均形成 raw score volume；
5. 可选乘以 Rayleigh 简化深度权重 `exp(-h / penetration_depth)`；
6. 最高得分位置作为科研级候选 `best_location`。

`score_volume` 保存于：

```text
arrays/arr_score_volume.npy
arrays/arr_score_volume_raw.npy
arrays/arr_score_volume_depth_weighted.npy
arrays/arr_scan_x_grid.npy
arrays/arr_scan_y_grid.npy
arrays/arr_scan_depth_grid.npy
```

## 基础置信度诊断

Stage 3 在扫描结果之后增加规则型基础诊断：

- `peak_sharpness`：最高峰相对局部背景是否尖锐；
- `score_contrast` 和 `score_percentile`：最高分相对全局得分体是否突出；
- `multi-shot consistency`：最佳点处各炮贡献是否均衡；
- `y-depth coupling warning`：检查单侧 DAS-like 几何下 y-depth 高分区是否拉长；
- `low_confidence_flag`：输出 `high / medium / low` 三档科研诊断标签。
- `best_depth_at_boundary_warning`：主 best 深度贴近扫描上下边界时触发；
- `wide_y_high_score_zone_warning`：best_x 附近 y 方向高分区过宽时触发；
- `raw_weighted_divergence_warning`：raw_best 与 weighted_best 三维位置差异过大时触发；
- `shallow_bias_warning`：depth weighting 将 weighted_best 明显推向浅部时触发。

输出文件：

```text
arrays/arr_confidence_metrics.json
figures/fig_confidence_diagnostics.png
figures/fig_raw_vs_weighted_best_location.png
figures/fig_raw_vs_weighted_x_depth_slice.png
figures/fig_y_high_score_width_check.png
reports/report_confidence.md
```

这些指标不是概率置信度，不是完整不确定性评价，也不能作为工程确诊结论。

## 物理自检图

- `fig_source_anomaly_receiver_path_section.png`：等效散射路径剖面示意，不是真实射线路径。
- `fig_rayleigh_depth_sensitivity.png`：Rayleigh 波深度敏感性近似示意。
- `fig_diffraction_travel_time_curves.png`：炮集上叠加直达波、真值绕射曲线和最佳点绕射曲线。

Rayleigh-wave diffraction 类思路的重点是绕射走时曲线和直达面波压制后的残余绕射能量，x-y 地表响应图只用于解释几何和传播趋势。

## 当前近似和限制

- 当前结果必须称为 `DAS-like response approximation`。
- 当前正演、伪波场和扫描都属于 `kinematic approximation`。
- 当前快照应称为 `kinematic_surface_response_snapshot` 或运动学地表响应示意图，不是弹性波方程数值模拟。
- GIF 是地表响应传播示意动图，不是真实全波场模拟。
- 当前速度模型为 `uniform effective Rayleigh velocity`。
- Rayleigh 深度敏感性权重不是严格模态深度核，只是波长量级的经验衰减。
- 当前 DAS-like 响应是点式接收近似，尚未实现真实 gauge length 响应。
- `best_location` 是运动学局部能量聚焦结果，不能作为工程确诊结论。
- 单侧 DAS-like 几何下，横向 y 和埋深 h 可能耦合。

后续阶段再做完整置信度、鲁棒性参数扫描、DAS gauge length、分层速度和局部全波场验证。
