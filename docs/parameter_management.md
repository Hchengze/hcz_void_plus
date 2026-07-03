# Parameter Management

`main.py` 是唯一参数中心。

## 禁止

- 不创建 `config` 文件夹。
- 不创建 `para` 文件夹。
- 不在 `src`、`experiments`、`visualization` 或 `pipeline` 中定义第二套默认参数。
- `run_debug.py` 不能维护第二套算法逻辑。

## Stage 2 新增参数

可视化和输出：

- `--figure-language`
- `--max-shot-gather-figures`
- `--save-wavefield-snapshots`
- `--save-wavefield-animation`
- `--wavefield-snapshot-count`
- `--wavefield-grid-nx`
- `--wavefield-grid-ny`
- `--wavefield-animation-fps`
- `--wavefield-shot-index`
- `--output-prefix-style`

扫描定位：

- `--scan-enabled`
- `--scan-x-min-m`
- `--scan-x-max-m`
- `--scan-x-step-m`
- `--scan-y-min-m`
- `--scan-y-max-m`
- `--scan-y-step-m`
- `--scan-depth-min-m`
- `--scan-depth-max-m`
- `--scan-depth-step-m`
- `--score-method`
- `--direct-mute-enabled`
- `--direct-mute-half-width-s`
- `--scan-time-window-half-width-s`
- `--scan-use-depth-weight`
- `--rayleigh-penetration-factor`
- `--wavelet-dominant-frequency-hz`

## Stage 3 新增参数

稳定成果导出：

- `--export-latest-stable`
- `--latest-stable-dirname`

基础置信度诊断：

- `--confidence-threshold-ratio`
- `--confidence-neighborhood-radius`
- `--consistency-warning-cv-threshold`
- `--coupling-warning-span-y-m`
- `--coupling-warning-span-depth-m`

这些参数仍然全部由 `main.py` 的 argparse 定义、派生和校验。`src/confidence`、`src/utils/stable_export.py` 和 pipeline 只接收解析后的 `params`，不维护第二套局部参数。

## 派生参数

`params.derived` 新增：

- `scan_x_grid`
- `scan_y_grid`
- `scan_depth_grid`
- `scan_shape`
- `scan_grid_point_count`
- `estimated_wavelength_m`
- `rayleigh_penetration_depth_m`
- `latest_stable_dir`

扫描网格总点数在 `main.py` 中校验，避免本地运行失控。
