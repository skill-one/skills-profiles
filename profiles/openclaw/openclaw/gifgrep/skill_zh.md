# gifgrep

使用 `gifgrep` 搜索 GIF 提供商（Tenor/Giphy），在 TUI 中浏览，下载结果，并提取静态图像或动画帧。

GIF-Grab (gifgrep 工作流程)

- 搜索 -> 预览 -> 下载 -> 提取（静态图像/动画帧）用于快速预览和分享。

快速入门

- `gifgrep cats --max 5`
- `gifgrep cats --format url | head -n 5`
- `gifgrep search --json cats | jq '.[0].url'`
- `gifgrep tui "办公室握手"`
- `gifgrep cats --download --max 1 --format url`

TUI + 预览

- TUI: `gifgrep tui "查询"`
- CLI 静态图像预览: `--thumbs` (仅适用于 Kitty/Ghostty；静态帧)

下载 + 预览

- `--download` 保存到 `~/Downloads`
- `--reveal` 在 Finder 中显示最后一个下载的文件

静态图像 + 动画帧

- `gifgrep still ./clip.gif --at 1.5s -o still.png`
- `gifgrep sheet ./clip.gif --frames 9 --cols 3 -o sheet.png`
- 动画帧 = 单个 PNG 网格，包含采样的帧（适用于快速预览、文档、PR、聊天）。
- 调整: `--frames` (数量), `--cols` (网格宽度), `--padding` (间距)。

提供商

- `--source auto|tenor|giphy`
- `GIPHY_API_KEY` 用于 `--source giphy` 时必须提供
- `TENOR_API_KEY` 可选（如果未设置，则使用 Tenor 演示密钥）

输出

- `--json` 打印结果数组 (`id`, `title`, `url`, `preview_url`, `tags`, `width`, `height`)
- `--format` 用于管道友好的字段（例如，`url`）

GIF 资产卫生

- 在推荐或使用动画 GIF URL 之前，验证它是否成功解析，具有 `Content-Type: image/gif`，并且实际上是动画的（多个帧或循环元数据；例如，使用 `file`、`identify` 或小型脚本检查）。
- 记录资产 attribution/license/source URL。
- 当需要本地资产时，不要使用热链接：将其下载/复制到项目中并引用本地文件。

环境调整

- `GIFGREP_SOFTWARE_ANIM=1` 强制使用软件动画
- `GIFGREP_CELL_ASPECT=0.5` 调整预览几何形状
