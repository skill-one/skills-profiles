# HeyGen API (已弃用)

> **此技能已弃用。** 请使用专注技能：
> - **`create-video`** — 从文本提示生成视频（视频代理 API）
> - **`avatar-video`** — 使用特定头像、声音、脚本和场景构建视频（v2 API）

此技能保留用于向后兼容，但将在未来的版本中移除。

---

AI 头像视频创建 API，用于生成口播视频、解说视频和演示文稿。

## 工具选择

如果可用 HeyGen MCP 工具（`mcp__heygen__*`），请**优先使用**它们，而不是直接 HTTP API 调用——它们会自动处理身份验证和请求格式化。

| 任务 | MCP 工具 | 备用（直接 API） |
|------|----------|----------------------|
| 从提示生成视频 | `mcp__heygen__generate_video_agent` | `POST /v1/video_agent/generate` |
| 检查视频状态 / 获取 URL | `mcp__heygen__get_video` | `GET /v2/videos/{video_id}` |
| 列出账户视频 | `mcp__heygen__list_videos` | `GET /v2/videos` |
| 删除视频 | `mcp__heygen__delete_video` | `DELETE /v2/videos/{video_id}` |

如果不可用 HeyGen MCP 工具，请使用带有 `X-Api-Key: $HEYGEN_API_KEY` 头的直接 HTTP API 调用，如参考文件中所述。

## 默认工作流程

**对于大多数视频请求，请优先使用视频代理。**
始终使用 [prompt-optimizer.md](references/prompt-optimizer.md) 指南来构建包含场景、时序和视觉风格的提示。

**使用 MCP 工具：**
1. 使用 [prompt-optimizer.md](references/prompt-optimizer.md) → [visual-styles.md](references/visual-styles.md) 编写优化后的提示
2. 调用 `mcp__heygen__generate_video_agent` 并传入提示和配置（duration_sec、orientation、avatar_id）
3. 调用 `mcp__heygen__get_video` 并传入返回的 video_id 以轮询状态并获取下载 URL

**不使用 MCP 工具（直接 API）：**
1. 使用 [prompt-optimizer.md](references/prompt-optimizer.md) → [visual-styles.md](references/visual-styles.md) 编写优化后的提示
2. `POST /v1/video_agent/generate` — 参见 [video-agent.md](references/video-agent.md)
3. `GET /v2/videos/<id>` — 参见 [video-status.md](references/video-status.md)

仅在用户明确需要以下功能时使用 v2/video/generate：
- 精确脚本，无需 AI 修改
- 特定 voice_id 选择
- 每个场景使用不同的头像/背景
- 精确的每场景时序控制
- 带有精确规格的程序化/批量生成

## 快速参考

| 任务 | MCP 工具 | 读取 |
|------|----------|------|
| 从提示生成视频（简单） | `mcp__heygen__generate_video_agent` | [prompt-optimizer.md](references/prompt-optimizer.md) → [visual-styles.md](references/visual-styles.md) → [video-agent.md](references/video-agent.md) |
| 带精确控制的生成视频 | — | [video-generation.md](references/video-generation.md)、[avatars.md](references/avatars.md)、[voices.md](references/voices.md) |
| 检查视频状态 / 获取下载 URL | `mcp__heygen__get_video` | [video-status.md](references/video-status.md) |
| 添加字幕或文本叠加 | — | [captions.md](references/captions.md)、[text-overlays.md](references/text-overlays.md) |
| 透明视频用于合成 | — | [video-generation.md](references/video-generation.md)（WebM 部分） |
| 与 Remotion 一起使用 | — | [remotion-integration.md](references/remotion-integration.md) |

## 参考文件

### 基础
- [references/authentication.md](references/authentication.md) - API 密钥设置和 X-Api-Key 头
- [references/quota.md](references/quota.md) - 信用系统和使用限制
- [references/video-status.md](references/video-status.md) - 轮询模式和下载 URL
- [references/assets.md](references/assets.md) - 上传图像、视频、音频

### 核心视频创建
- [references/avatars.md](references/avatars.md) - 列出头像、样式、avatar_id 选择
- [references/voices.md](references/voices.md) - 列出声音、区域、速度/音调
- [references/scripts.md](references/scripts.md) - 编写脚本、暂停、节奏
- [references/video-generation.md](references/video-generation.md) - POST /v2/video/generate 和多场景视频
- [references/video-agent.md](references/video-agent.md) - 单次提示视频生成
- [references/prompt-optimizer.md](references/prompt-optimizer.md) - 编写有效的视频代理提示（核心工作流程 + 规则）
- [references/visual-styles.md](references/visual-styles.md) - 20 种命名视觉风格，包含完整规格
- [references/prompt-examples.md](references/prompt-examples.md) - 完整生产提示示例 + 即用模板
- [references/dimensions.md](references/dimensions.md) - 分辨率和宽高比

### 视频定制
- [references/backgrounds.md](references/backgrounds.md) - 纯色、图像、视频背景
- [references/text-overlays.md](references/text-overlays.md) - 添加带字体和定位的文本
- [references/captions.md](references/captions.md) - 自动生成的字幕

### 高级功能
- [references/templates.md](references/templates.md) - 模板列表和变量替换
- [references/photo-avatars.md](references/photo-avatars.md) - 从照片创建头像
- [references/webhooks.md](references/webhooks.md) - Webhook 端点和事件

### 集成
- [references/remotion-integration.md](references/remotion-integration.md) - 在 Remotion 合成中使用 HeyGen
