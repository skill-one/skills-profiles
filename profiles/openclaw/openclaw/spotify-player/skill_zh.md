# spogo / spotify_player

使用 `spogo` **(推荐)** 进行 Spotify 播放/搜索。如有需要，可回退使用 `spotify_player`。

要求

- Spotify 高级账户。
- 安装 `spogo` 或 `spotify_player` 中的任意一个。

spogo 设置

- 导入 Cookie：`spogo auth import --browser chrome`

常用 CLI 命令

- 搜索：`spogo search track "查询"`
- 播放：`spogo play|pause|next|prev`
- 设备：`spogo device list`, `spogo device set "<名称|ID>"`
- 状态：`spogo status`

spotify_player 命令（回退）

- 搜索：`spotify_player search "查询"`
- 播放：`spotify_player playback play|pause|next|previous`
- 连接设备：`spotify_player connect`
- 点赞曲目：`spotify_player like`

备注

- 配置文件夹：`~/.config/spotify-player`（例如，`app.toml`）。
- 为启用 Spotify Connect 集成，请在配置中设置用户 `client_id`。
- 应用程序中可通过 `?` 使用 TUI 快捷键。
