# hcz_void_plus

城市道路既有通信光纤 DAS 空洞探测科研级算法原型平台。

本项目面向道路地下空洞、脱空、松散区、管沟、管线周边扰动、弱夹层和破碎带等浅层异常体。典型几何为单侧 DAS-like 接收：光纤沿道路方向布设，近似位于 `y = 0`；震源线位于道路另一侧或道路边缘，近似位于 `y = W`；异常体位于道路下方 `(x0, y0, h)`。

## 当前已实现能力

- `main.py` 统一入口与 argparse 参数中心。
- 道路、光纤、震源、异常体和时间采样的派生参数统一解析。
- 坐标约定：`x` 沿道路和光纤方向，`y` 横穿道路方向，`z` 深度向下为正。
- 均匀等效瑞雷波速度模型：`uniform effective Rayleigh velocity`。
- Ricker 子波、直达瑞雷波、异常体等效散射/绕射波。
- 多炮数据输出形状：`shot × time × channel`。
- point receiver 级别的 `DAS-like response approximation`。
- 输出数组、metadata、参数快照、几何图、炮集图和 Markdown 报告。
- pytest 基础测试。

## 如何运行

如果系统 PATH 中有 Python：

```bash
python main.py --task debug
python main.py --task forward
python main.py --task full_pipeline
```

当前本机环境可使用：

```bash
D:\HczApp\Anaconda\envs\mywork\python.exe main.py --task debug
D:\HczApp\Anaconda\envs\mywork\python.exe main.py --task forward
```

小规模调试入口：

```bash
D:\HczApp\Anaconda\envs\mywork\python.exe run_debug.py
```

## 输出结果

每次运行会在 `outputs/<run_name>_<timestamp>/` 下创建独立目录，典型内容包括：

- `params_snapshot.json`
- `metadata.json`
- `saved_arrays/synthetic_data.npy`
- `saved_arrays/time_axis.npy`
- `saved_arrays/channel_x.npy`
- `saved_arrays/shot_x.npy`
- `figures/geometry.png`
- `figures/shot_gather_*.png`
- `reports/forward_report.md`
- `logs/run_log.txt`

## 当前近似条件

- 当前结果必须称为 `DAS-like response approximation`。
- 当前第一阶段采用 `kinematic approximation`。
- 当前速度模型为 `uniform effective Rayleigh velocity`。
- 多个散射点表示异常体形状是运动学等效散射近似，不是真实边界散射模拟。
- gauge length 已进入统一参数和 metadata，但在 point receiver 模式下不参与波形计算。

## 不是什么

- 不是完整 DAS 仪器模拟。
- 不是完整三维弹性波全波场模拟。
- 不是可安装发布的软件包。
- 不是工业级工程确诊软件。
- 当前结果不能作为工程确诊结论。

## 后续路线

后续阶段将逐步加入多炮扫描定位、绕射/散射识别、置信度评价、鲁棒性分析、DAS gauge length 响应、分层速度模型和局部全波场验证。
