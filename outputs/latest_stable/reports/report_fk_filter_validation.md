# FK / f-v 滤波验证报告

当前 FK 滤波是简化速度扇区 QC，不是成熟面波 FK 分离软件。

- strict FK applicable: `True`
- warning: 无
- direct wave reduction ratio: `0.03166`
- diffraction preservation ratio: `0.9797`
- shape preserved: `True`

## 解释

- direct wave reduction ratio 越高，说明直达波局部能量削弱越明显。
- diffraction preservation ratio 接近或大于 1，说明理论绕射曲线附近能量没有被明显误伤。
- receiver 不是 straight 或通道非均匀时，f-k 解释只能作为近似 QC。