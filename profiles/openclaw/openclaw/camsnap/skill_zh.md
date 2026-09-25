# camsnap

使用 `camsnap` 从配置的摄像头中抓取快照、片段或运动事件。

## 安装

- 配置文件：`~/.config/camsnap/config.yaml`
- 添加摄像头：`camsnap add --name kitchen --host 192.168.0.10 --user user --pass pass`

## 常用命令

- 发现：`camsnap discover --info`
- 快照：`camsnap snap kitchen --out shot.jpg`
- 片段：`camsnap clip kitchen --dur 5s --out clip.mp4`
- 运动监控：`camsnap watch kitchen --threshold 0.2 --action '...'`
- 诊断：`camsnap doctor --probe`

## 本地网络摄像头（macOS）

- 列出设备：`camsnap devices`
- 从本地摄像头抓取快照：`camsnap snap --device 0 --out webcam.jpg`
- PTZ 位置和范围：`camsnap ptz status --device 0`
- 移动云台摄像头：`camsnap ptz goto --device 0 --pan 45 --tilt -18`
- 还支持 `camsnap ptz move`（相对增量）和 `camsnap ptz home`。

## 注意事项

- 需要 `ffmpeg` 在 PATH 路径中。
- 建议在录制较长的片段前进行短时间测试抓取。
- PTZ 需要 macOS 摄像头权限：这些摄像头在流媒体传输时仅服务 UVC 控制，因此 `camsnap` 会为操作保持捕获会话打开。
- 运动命令会验证稳定位置，如果摄像头未达到该位置则非零退出。机载 AI 帧面可以覆盖手动定位；如果移动持续丢失，请禁用跟踪。
