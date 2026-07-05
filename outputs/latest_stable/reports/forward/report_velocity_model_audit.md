# 速度模型主线审计报告

本报告检查 layered / heterogeneous 等效 Rayleigh 速度模型是否真正进入主流程，
而不是只停留在 `src/model/` 文件中。

- 当前 active velocity_model_type：`layered`
- argparse / full_pipeline velocity_model_type：`layered`
- 是否确认为 layered：`True`
- direct wave 使用 travel-time 接口：`True`
- scatter wave 使用 travel-time 接口：`True`
- scan candidate 使用 travel-time 接口：`True`
- layer depths m：`[0.3, 1.0, 3.0, 8.0]`
- layer velocities m/s：`[120.0, 180.0, 260.0, 350.0]`

## representative velocity 调用点

- `src/forward/kinematic_baseline.py`：合法 baseline 使用。
- `src/model/velocity_model.py`：诊断/metadata/兼容用途，需要继续人工关注。
- `src/pipeline/run_forward_pipeline.py`：诊断/metadata/兼容用途，需要继续人工关注。

## uniform 与 active model 走时差异

- direct RMS 差异：`268.9` ms
- direct 最大绝对差异：`500.2` ms
- scatter RMS 差异：`73.79` ms
- scatter 最大绝对差异：`102.4` ms

## elastic2d 说明

elastic2d_prototype 使用独立 Vp/Vs/rho 弹性参数；它与 layered_kinematic 的 Rayleigh equivalent velocity model 不是同一套物理参数。

当前结果仍是 straight-ray kinematic approximation 与 validation prototype，不能写成工程确诊。