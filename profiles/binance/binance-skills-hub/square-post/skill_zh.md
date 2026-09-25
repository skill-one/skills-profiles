# Square Post 技能

## 目的

通过运行 `scripts/` 目录下的本地脚本将新内容发布到 Binance Square。

支持的发布类型：
- 纯文本短帖
- 带有最多 4 张图片的图片帖
- 带标题（可选封面图）的长文章
- 带自动生成封面图的视频帖

请勿手动编写 API 请求进行常规发布。脚本负责上传、轮询、封面生成和发布行为。

## 运行时依赖

- Node.js 18 或更高版本。脚本使用原生 ES 模块和内置的 `fetch` API。
- `ffmpeg` 是视频帖所必需的，因为 `post-video.mjs` 会提取第一帧作为封面图。
- 当用户未提供视频时长时，需要 `ffprobe`。
- 网络访问是 Binance Square OpenAPI 请求和预签名媒体上传所必需的。

## 认证

发布需要 Binance Square OpenAPI 密钥。

发布前：
- 优先使用用户环境变量中的 `BINANCE_SQUARE_OPENAPI_KEY`（如果存在）。
- 如果不存在，脚本会自动检查 `~/.config/binance-square/openapi-key`。
- 如果未找到有效密钥，先提示用户提供 API 密钥。
- 如果用户希望在后续请求中重用密钥，请使用 `BINANCE_SQUARE_OPENAPI_KEY=<apiKey> node scripts/save-key.mjs` 保存；否则仅用于当前命令环境。
- 告知用户可以在以下地址创建 API 密钥：https://www.binance.com/square/creator-center/home

仅通过 `BINANCE_SQUARE_OPENAPI_KEY`（环境变量或保存的文件）传递密钥。切勿将密钥写入命令参数或打印完整密钥——CLI 参数会出现在 `ps` 输出和 shell 历史记录中。提及密钥时，仅显示前 5 位和最后 4 位，例如 `abc12...xyz9`。

## 脚本

所有命令应从该技能目录运行。

### 文本或文章发布

用于纯文本短帖或无图片的长文章。

```bash
node scripts/post-text.mjs --text "Hello #crypto $BTC"
```

带标题且无封面的长文章：

```bash
node scripts/post-text.mjs --text "Full article body..." --title "Market Report"
```

标志：
- `--text` 必填，发布文本内容
- `--title` 可选，设置文章风格内容

### 图片发布

用于短图片帖或带封面图的长文章。

```bash
node scripts/post-image.mjs --text "Chart analysis" --images "./chart1.png,./chart2.png"
```

带标题和封面的长文章：

```bash
node scripts/post-image.mjs --text "Full analysis..." --title "Market Report" --cover "./chart.png"
```

标志：
- `--text` 必填，发布或文章内容
- `--images` 短图片帖必填。使用逗号分隔的图片路径，最多 4 张。
- `--title` 可选，设置文章风格内容。存在时，不传递 `--images`。
- `--cover` 当 `--title` 存在时，文章带媒体必填。文章模式支持且仅支持一张封面图。

脚本上传每张图片，等待处理，并使用后端返回的图片 URL 发布。如果提供 `--title`，则发布 `contentType=2`，需要 `--cover`，并将上传的图片 URL 作为 `cover` 发送。如果未提供 `--title`，则发布 `contentType=1` 并发送所有 `--images` 作为 `imageList`。

### 视频发布

用于视频帖。

```bash
node scripts/post-video.mjs --video "./video.mp4" --duration 7.5 --text "My analysis"
```

标志：
- `--video` 必填，本地视频路径
- `--duration` 必填，视频时长（秒）
- `--text` 可选，发布文本内容

脚本上传视频，等待处理，使用 `ffmpeg` 提取第一帧作为封面图，并包含 `cover` 在请求中发布。

如果用户未提供时长，请在运行脚本前使用 `ffprobe` 确定。

## 代理工作流程

1. 解析 API 密钥（见认证）。如果未解析，在执行任何操作前先停止并提示用户。

2. 根据下表从用户意图选择脚本，并验证约束——如果约束被违反，解释并停止运行。

   | 用户意图 | 脚本 | 必填标志 |
   |---|---|---|
   | 短文本帖 | `post-text.mjs` | `--text` |
   | 长文章，无媒体 | `post-text.mjs` | `--text --title` |
   | 图片短帖（1-4 张图片，无标题） | `post-image.mjs` | `--text --images "<p1,p2,...>"` |
   | 带封面文章 | `post-image.mjs` | `--text --title --cover` |
   | 视频帖 | `post-video.mjs` | `--video --duration` (+ 可选 `--text`) |

3. 运行前消除歧义：
   - 标题 + 恰好一张图片 → 该图片为封面 (`--cover`，不是 `--images`)。
   - 标题 + 多张图片 → 停止并询问哪张图片为封面。
   - 无时长的视频 → 先运行 `ffprobe` 获取时长。

4. 精确保留用户内容。不要重写、翻译、添加话题标签/货币标签或更改标点符号。`$coin` 和 `#topic` 文本将原样通过——后端会解析它们。

5. 使用 `BINANCE_SQUARE_OPENAPI_KEY` 注入命令环境一次性使用（绝不作为 CLI 参数）运行脚本。

6. 报告结果：
   - 成功时，返回脚本打印的 `ID` 和 `Link`。
   - 如果脚本打印 `Success!` 但 `ID: unavailable` 和 `Link: unavailable`，视为成功——`/content/add` 提交后返回 504，因此没有帖子 ID 或链接。
   - 失败时，显示脚本错误和任何 API 代码/消息。

## 约束

- 图片：每帖最多 4 张；文章封面必须且仅 1 张图片。
- 视频：每帖最多 1 个。
- 图片和视频在单帖中互斥。
- 仅附加用户明确提供的媒体；不要自动附加。
- 不要修改用户提供的文本。`#topic` 和 `$coin` 由服务器端解析。
- 每日限制：每日 100 帖，每日 400 上传。

## 常见错误

- `220003`：API 密钥未找到。
- `220004`：API 密钥过期。
- `220009`：OpenAPI 每日发布限制超出。
- `220014`：每日上传限制超出。
- `20002` 或 `20022`：检测到敏感词。
- `20013`：内容长度受限。
- `20020` 或 `220011`：内容主体不能为空。
- `30008`、`2000001` 或 `2000002`：账户或设备发布限制。

## 范围

该技能仅支持发布新帖。不支持：
- 读取、列出或搜索现有帖子
- 编辑或删除帖子
- 评论、点赞或其他交互
- 用户资料或账户管理
- 定时或草稿
