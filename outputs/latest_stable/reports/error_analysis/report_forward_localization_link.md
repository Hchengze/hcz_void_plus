# forward-localization link 报告

本报告连接三维运动学体响应 proxy、炮集理论绕射到时和 posterior-like 定位结果。
当前结果仍是科研候选区，不是工程确诊。

- forward_localization_link_status = `warning`
- volume_peak_to_truth_distance_m = `50.75367307192268`
- posterior_peak_to_truth_distance_m = `8.558621384311845`
- volume_peak_to_posterior_peak_distance_m = `42.36081740734436`
- posterior_vs_truth_scatter_curve_rms_ms = `39.33348544547595`

## 可能原因

- geometry ambiguity or attribute weighting
- attenuation changes amplitude ranking

## 限制

- 三维体响应是 kinematic proxy，不是真实 3D elastic wavefield。
- 单侧 DAS-like 几何仍可能导致 y-depth ambiguity。
- attenuation 会改变振幅排序，不能被误读为真实粘弹性传播。