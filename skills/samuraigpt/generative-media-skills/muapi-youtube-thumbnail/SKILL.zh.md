---
name: muapi-youtube-thumbnail
description: 设计一个高点击率的YouTube缩略图——使用引人注目的图像、大胆的文字布局，并在必要时加入富有情感的面部/主题。
---

# YouTube 缩略图

**设计高点击率的 YouTube 缩略图 — 震撼的视觉元素、醒目的文字布局，如有需要可加入富有情感的面部/主题。**

## 输入

| 名称 | 类型 | 必填 | 默认值 | 描述 |
|:---|:---|:---|:---|:---|
| `title` | 文本 | 是 | — | 视频标题或主题（例如："在 24 小时内尝试了 7 个 AI 工具 — 发生了什么"）。 |
| `channel_style` | 文本 | 否 | 粗体、高对比度、亮色、简洁设计、YouTube 科技美学 | 频道品牌风格（例如："暗黑忧郁游戏"、"明亮教育"、"极简企业"）。 |
| `subject_description` | 文本 | 否 | — | 可选的人或主题描述（例如："穿着连帽衫的惊讶年轻人"）。 |

## 步骤

缩略图是 YouTube 点击率的首要因素。生成一张最大冲击力的 16:9 图像。

### 阶段 A — 规划构图

在生成前，简要思考最适合此主题的缩略图公式：
- **情感优先**：如果相关，加入震惊/好奇的面部 + 醒目文字 = 高点击率
- **文字叠加**：最多 3-5 个字，高对比度（深色背景上的白/黄色，或反之）
- **对比度与饱和度**：缩略图在网格中竞争 — 它们必须突出

### 阶段 B — 生成缩略图

1. 构建图像生成提示：
   - 主题：如果提供了 `{{subject_description}}`，则设计一个能戏剧化表现主题的对象/场景。
   - 氛围：源自 `{{channel_style}}`。
   - 构图：三分法，主体在左侧或右侧，留出文字空间。
   - 风格标签：`{{channel_style}}, youtube thumbnail composition, ultra detailed, vibrant, high contrast, 16:9`。
2. 调用 `muapi image generate` (model=gpt-image-2-text-to-image, aspect_ratio=16:9)。

### 阶段 C — 文字叠加指导

生成后，返回：
- **建议叠加文字**：3-5 个与标题 `{{title}}` 相辅相成的粗体字。
- **文字位置**：在画布上的位置（例如："醒目的黄色文字，右上三分之一"）。
- **字体建议**：风格建议（例如："Impact 风格大写字母，带黑色轮廓"）。

## 注意事项
- 不要在提示中放入过多文字 — 图像模型中的文字渲染不可靠。指导用户在后期制作中添加文字（Canva、Photoshop）。
- 如果用户会话中已有频道图像或面部照片，使用 `muapi image edit` 来整合它。
- 只有在用户要求时才建议 A/B 变体。

## 触发关键词

`youtube thumbnail`, `yt thumbnail`, `thumbnail`, `video thumbnail`, `youtube cover`

---

## 执行代理注意事项

- 此流程由 LLM 协调：读取每个阶段，从用户那里收集任何缺失的输入，然后调用 `muapi` CLI 命令。如果 `MUAPI_API_KEY` 未设置，先使用 `muapi auth configure`。
- 对于尚无 CLI 别名的模型 ID，通过 `curl -X POST https://api.muapi.ai/api/v1/<endpoint> -H "x-api-key: $MUAPI_API_KEY" -H 'content-type: application/json' -d '{...}'` 落回原始端点，并使用 `muapi predict wait <request_id>` 进行轮询。
- 在发出每次调用前，将 `{{input_name}}` 占位符替换为用户的实际输入。
