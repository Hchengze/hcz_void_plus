# Parameter Management

`main.py` 是唯一参数中心。

## 规则

- 不创建 `config` 文件夹。
- 不创建 `para` 文件夹。
- 所有默认参数、命令行参数、参数派生和参数校验统一放在 `main.py`。
- 算法模块、绘图模块和实验脚本只能接收 `main.py` 解析后的 `params` 对象。
- `run_debug.py` 只能调用 `main()`，不能维护第二套算法逻辑。

## 派生参数

`params.derived` 至少包含：

- `channel_x`
- `receiver_xyz`
- `shot_x`
- `source_xyz`
- `time_axis`
- `nt`
- `fiber_x_end_m`
- `source_x_end_m`
- `gauge_channel_count`
- `output_run_dir`

`fiber.channel_count` 和 `source.shot_count` 是主参数，末端坐标由程序自动计算。`source_y_m` 未显式设置时，自动等于 `road_width_m`。
