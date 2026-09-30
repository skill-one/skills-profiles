---
name: camsnap
description: 从RTSP/ONVIF摄像机和本地网络摄像头捕获帧或片段，包括USB云台控制。
---

# camsnap

使用 `camsnap` 从配置的摄像头中抓取快照、片段或运动事件。

设置

- 配置文件：`~/.config/camsnap/config.yaml`
- 添加摄像头：`camsnap add --name kitchen --host 192.168.0.10 --user user --pass pass`

常用命令

- 发现：`camsnap discover --info`
- 快照：`camsnap snap kitchen --out shot.jpg`
- 片段：`camsnap clip kitchen --dur 5s --out clip.mp4`
- 运动监控：`camsnap watch kitchen --threshold 0.2 --action '...'`
- 诊断：`camsnap doctor --probe`

本地网络摄像头（macOS）

- 列出设备：`camsnap devices`
- 从本地摄像头抓取快照：`camsnap snap --device 0 --out webcam.jpg`
- PTZ 位置和范围：`camsnap ptz status --device 0`
- 移动云台摄像头：`camsnap ptz goto --device 0 --pan 45 --tilt -18`
- 还支持 `camsnap ptz move`（相对增量）和 `camsnap ptz home`。

注意事项

- 需要 `ffmpeg` 在 PATH 路径中。
- 建议在录制较长的片段前进行短时间测试抓取。
- PTZ 需要 macOS 摄像头权限：这些摄像头在流媒体传输时仅服务 UVC 控制，因此 `camsnap` 会为操作保持抓取会话开启。
- 运动命令会验证稳定位置，如果摄像头未达到该位置则退出并返回非零值。机载 AI 帧面可以覆盖手动定位；如果移动持续丢失目标，请禁用跟踪。
