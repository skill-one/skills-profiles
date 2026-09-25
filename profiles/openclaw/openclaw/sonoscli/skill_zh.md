# Sonos 命令行工具

使用 `sonos` 命令控制本地网络中的 Sonos 音响设备。

## 快速入门

- `sonos discover`
- `sonos status --name "厨房"`
- `sonos play|pause|stop --name "厨房"`
- `sonos volume set 15 --name "厨房"`

## 常用任务

- 组合：`sonos group status|join|unjoin|party|solo`
- 收藏：`sonos favorites list|open`
- 播放队列：`sonos queue list|play|clear`
- Spotify 搜索（通过 SMAPI）：`sonos smapi search --service "Spotify" --category tracks "查询内容"`

## 注意事项

- 如果 SSDP 失败，请指定 `--ip <speaker-ip>`。
- Spotify Web API 搜索是可选的，需要 `SPOTIFY_CLIENT_ID/SECRET`。
- 如果出现错误，请查看故障排除部分，并在有合适匹配的情况下提供建议。

## 故障排除

### `sonos discover` - `no route to host`

- 当出现错误 `Error: write udp4 0.0.0.0:64326->239.255.255.250:1900: sendto: no route to host (Command exited with code 1)` 时
  - 注意 `0.0.0.0:` 后面的端口号是临时的，会变化，子网掩码可能也不完全匹配
  - `sendto: no route to host` 应保持一致
- 建议用户在 Mac OS 的 `direct`（无 Docker 沙盒）模式下，需要在设置 -> 隐私与安全性 -> 本地网络中启用 Gateway 的顶层主机父进程
  - 如果通过 `launchd` 运行，则为 `node`
  - 如果直接在终端运行 Gateway，则为 `Terminal`
  - 如果通过 VS Code 终端运行，则为 `Visual Studio Code`
- 另一个选项是使用允许该沙盒网络访问的 `sandbox`（docker 容器）

### `sonos discover` - `bind: operation not permitted`

- 当出现错误 `Error: listen udp4 0.0.0.0:0: bind: operation not permitted`
- 建议用户可能正在通过 Codex 或其他不允许网络访问的沙盒运行（这可以通过在启用沙盒的 Codex CLI 会话中运行 `sonos discover` 并不批准提升请求来复现）
