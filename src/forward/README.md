# src/forward 职责说明

`src/forward/` 是 forward modeling 研发区，不等同于当前稳定推荐入口。Stage 5C 后，本目录职责如下。

## 当前 active engine

- `layered_kinematic.py`
- engine name：`layered_kinematic`
- role：当前主定位 forward，使用 `velocity_model` 的 straight-ray 路径采样积分。
- boundary：仍是 kinematic approximation，不是 3D elastic wavefield。

## baseline engine

- `kinematic_baseline.py`
- engine name：`kinematic_baseline`
- role：F0 快速均匀速度运动学基线，用于回归测试和对比。
- boundary：不能作为当前推荐主线。

## validation forward

- `acoustic2d/`
- engine name：`acoustic2d_prototype`
- role：声学波动方程基础设施验证。
- boundary：不能真实模拟 Rayleigh wave。

- `elastic2d/`
- engine name：`elastic2d_prototype`
- role：Rayleigh/free-surface/void scattering 的局部物理验证起点。
- boundary：最小科研原型，不是工业级 elastic 模拟，不替代主定位流程。

## 历史兼容或基础组件

- `direct_wave.py`：直达波运动学基础组件，被 F0/F1 调用；不要直接当作 engine。
- `scatter_kinematic.py`：等效散射运动学基础组件，被 F0/F1 调用；不要直接当作 engine。
- `multishot_forward.py`：组合 direct/scatter/DAS-like response 的兼容基础组件；不要直接当作当前推荐 engine。
- `wavelet.py`：通用 Ricker 子波工具，可保留。

## 统一入口

所有 forward engine 的选择应通过 `forward_registry.py`。`code/current_3d_algorithm/stable_forward.py` 只暴露当前稳定主线 `layered_kinematic`，并把 acoustic2d/elastic2d 明确标为 validation forward。
