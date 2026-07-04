# repository health 报告

- 当前 HEAD commit：`0d39007`
- latest_stable summary commit：`0d39007`
- latest_stable 是否为 Stage 5F：`True`
- latest_stable 是否混入旧阶段主结论：`False`
- figures 根目录 PNG 数量：`0`
- reports 根目录 MD 数量：`0`
- 状态：`pass`

## figures 分层数量

- `core`：`5`
- `forward`：`10`
- `localization`：`3`
- `uncertainty`：`3`
- `diagnostics`：`9`

## reports 分层数量

- `core`：`7`
- `forward`：`6`
- `localization`：`1`
- `uncertainty`：`0`
- `diagnostics`：`4`

## text health 关键统计

| file | lines | cr_only | longest | healthy |
|---|---:|---:|---:|---|
| `README.md` | 95 | 0 | 168 | True |
| `main.py` | 1036 | 0 | 203 | True |
| `docs/forward_modeling_roadmap.md` | 59 | 0 | 278 | True |
| `docs/forward_modeling_boundary.md` | 31 | 0 | 150 | True |
| `docs/elastic2d_forward_design.md` | 47 | 0 | 271 | True |
| `src/forward/acoustic2d/acoustic_fdtd.py` | 88 | 0 | 107 | True |
| `src/forward/forward_registry.py` | 102 | 0 | 107 | True |
| `code/current_3d_algorithm/stable_api.py` | 91 | 0 | 123 | True |
| `outputs/latest_stable/summary.md` | 229 | 0 | 718 | True |
| `outputs/latest_stable/reports/core/report_figure_deduplication.md` | 9 | 0 | 14 | True |
| `outputs/latest_stable/reports/core/report_figure_language_check.md` | 13 | 0 | 75 | True |
| `outputs/latest_stable/reports/core/report_figure_quality_check.md` | 43 | 0 | 91 | True |
| `outputs/latest_stable/reports/core/report_full_pipeline.md` | 73 | 0 | 362 | True |
| `outputs/latest_stable/reports/core/report_latest_stable_file_audit.md` | 27 | 0 | 43 | True |
| `outputs/latest_stable/reports/core/report_repository_health.md` | 57 | 0 | 110 | True |
| `outputs/latest_stable/reports/core/report_scientific_figure_self_check.md` | 34 | 0 | 66 | True |
| `outputs/latest_stable/reports/diagnostics/report_model_mismatch.md` | 19 | 0 | 164 | True |
| `outputs/latest_stable/reports/diagnostics/report_velocity_model_audit.md` | 32 | 0 | 109 | True |
| `outputs/latest_stable/reports/diagnostics/report_velocity_model_physics_bridge.md` | 20 | 0 | 101 | True |
| `outputs/latest_stable/reports/diagnostics/report_velocity_model_visualization.md` | 17 | 0 | 97 | True |
| `outputs/latest_stable/reports/forward/report_elastic2d_boundary_validation.md` | 29 | 0 | 148 | True |
| `outputs/latest_stable/reports/forward/report_elastic2d_das_response.md` | 28 | 0 | 83 | True |
| `outputs/latest_stable/reports/forward/report_elastic2d_free_surface_validation.md` | 29 | 0 | 148 | True |
| `outputs/latest_stable/reports/forward/report_elastic2d_rayleigh_benchmark.md` | 29 | 0 | 148 | True |
| `outputs/latest_stable/reports/forward/report_elastic2d_void_scattering.md` | 17 | 0 | 76 | True |
| `outputs/latest_stable/reports/forward/report_forward_engine_ablation.md` | 33 | 0 | 111 | True |
| `outputs/latest_stable/reports/localization/report_multi_attribute_ablation.md` | 16 | 0 | 104 | True |

- CR-only 文件：`[]`
- 真实一行化/极少行文件：`[]`

GitHub 网页 raw/preview 可能受编码或浏览器渲染影响；本报告以 git ls-tree、本地字节换行和 Python UTF-8 读取结果为准。