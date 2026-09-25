# Nano Banana Pro 图像生成与编辑

使用 Google 的 Nano Banana Pro API（Gemini 3 Pro 图像）生成新图像或编辑现有图像。

## 使用方法

使用绝对路径运行脚本（首先不要 cd 到技能目录）：

**生成新图像：**
```bash
uv run ~/.claude/skills/nano-banana-pro/scripts/generate_image.py --prompt "你的图像描述" --filename "输出文件名.png" [--resolution 1K|2K|4K] [--api-key KEY]
```

**编辑现有图像：**
```bash
uv run ~/.claude/skills/nano-banana-pro/scripts/generate_image.py --prompt "编辑说明" --filename "输出文件名.png" --input-image "路径/到/输入图像.png" [--resolution 1K|2K|4K] [--api-key KEY]
```

**重要提示：** 始终从用户当前工作目录运行脚本，以便图像保存在用户的工作位置，而不是技能目录中。

## 分辨率选项

Gemini 3 Pro 图像 API 支持 3 种分辨率（需要大写 K）：

- **1K**（默认）- 约 1024px 分辨率
- **2K** - 约 2048px 分辨率
- **4K** - 约 4096px 分辨率

将用户请求映射到 API 参数：
- 未提及分辨率 → `1K`
- "低分辨率"、"1080"、"1080p"、"1K" → `1K`
- "2K"、"2048"、"正常"、"中等分辨率" → `2K`
- "高分辨率"、"高-res"、"hi-res"、"4K"、"ultra" → `4K`

## API 密钥

脚本按以下顺序检查 API 密钥：
1. `--api-key` 参数（如果用户在聊天中提供了密钥）
2. `GEMINI_API_KEY` 环境变量

如果两者都不可用，脚本将退出并显示错误消息。

## 文件名生成

使用以下模式生成文件名：`yyyy-mm-dd-hh-mm-ss-name.png`

**格式：** `{时间戳}-{描述性名称}.png`
- 时间戳：当前日期/时间，格式为 `yyyy-mm-dd-hh-mm-ss`（24 小时制）
- 名称：描述性小写文本，用连字符分隔
- 保持描述部分简洁（通常 1-5 个词）
- 使用用户提示或对话中的上下文
- 如果不明确，使用随机标识符（例如，`x9k2`、`a7b3`）

示例：
- 提示 "一个宁静的日式花园" → `2025-11-23-14-23-05-japanese-garden.png`
- 提示 "山脉日落" → `2025-11-23-15-30-12-sunset-mountains.png`
- 提示 "创建一个机器人的图像" → `2025-11-23-16-45-33-robot.png`
- 上下文不明确 → `2025-11-23-17-12-48-x9k2.png`

## 图像编辑

当用户想要修改现有图像时：
1. 检查他们是否提供图像路径或在当前目录中引用图像
2. 使用 `--input-image` 参数与图像路径
3. 提示应包含编辑说明（例如，"让天空更戏剧化"、"移除人物"、"改为卡通风格")
4. 常见编辑任务：添加/移除元素、改变风格、调整颜色、模糊背景等

## 提示处理

**对于生成：** 将用户的图像描述原样传递给 `--prompt`。只有当明显不足时才重新处理。

**对于编辑：** 在 `--prompt` 中传递编辑说明（例如，"在天空添加彩虹"、"让它看起来像水彩画")

在两种情况下都保留用户的创意意图。

## 输出

- 将 PNG 保存到当前目录（如果文件名包含目录，则保存到指定路径）
- 脚本输出生成图像的完整路径
- **不要重新读取图像** - 只需告知用户保存的路径

## 示例

**生成新图像：**
```bash
uv run ~/.claude/skills/nano-banana-pro/scripts/generate_image.py --prompt "一个带有樱花宁静的日式花园" --filename "2025-11-23-14-23-05-japanese-garden.png" --resolution 4K
```

**编辑现有图像：**
```bash
uv run ~/.claude/skills/nano-banana-pro/scripts/generate_image.py --prompt "让天空更戏剧化，带有风暴云" --filename "2025-11-23-14-25-30-dramatic-sky.png" --input-image "original-photo.jpg" --resolution 2K
```
