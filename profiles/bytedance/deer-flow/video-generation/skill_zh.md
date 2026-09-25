# 视频生成技能

## 概述

该技能使用结构化提示和 Python 脚本生成高质量视频。工作流程包括创建 JSON 格式的提示，并执行带可选参考图像的视频生成。

## 核心功能

- 创建用于 AIGC 视频生成的结构化 JSON 提示
- 支持参考图像作为指导或视频的第一帧/最后一帧
- 通过自动化 Python 脚本执行生成视频

## 工作流程

### 第 1 步：理解需求

当用户请求视频生成时，识别：

- 主题/内容：图像中应包含什么
- 风格偏好：艺术风格、情绪、调色板
- 技术规格：宽高比、构图、光照
- 参考图像：任何用于指导生成的图像
- 无需检查 `/mnt/user-data` 下面的文件夹

### 第 2 步：创建结构化提示

在 `/mnt/user-data/workspace/` 生成结构化 JSON 文件，命名模式：`{描述性名称}.json`

### 第 3 步：创建参考图像（当图像生成技能可用时可选）

为视频生成生成参考图像。

- 如果只提供 1 张图像，则将其用作视频的引导帧

### 第 3 步：执行生成

调用 Python 脚本：
```bash
python /mnt/skills/public/video-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/prompt-file.json \
  --reference-images /path/to/ref1.jpg \
  --output-file /mnt/user-data/outputs/generated-video.mp4 \
  --aspect-ratio 16:9
```

参数：

- `--prompt-file`：JSON 提示文件的绝对路径（必填）
- `--reference-images`：参考图像的绝对路径（可选）
- `--output-file`：输出图像文件的绝对路径（必填）
- `--aspect-ratio`：生成图像的宽高比（可选，默认：16:9）

[!NOTE]
不要读取 python 文件，只需用参数调用它。

## 视频生成示例

用户请求："生成《纳尼亚传奇：狮子、女巫和魔衣橱》开场的短片"

第 1 步：在线搜索《纳尼亚传奇：狮子、女巫和魔衣橱》的开场场景

第 2 步：创建包含以下内容的 JSON 提示文件：
```json
{
  "title": "纳尼亚传奇 - 火车站告别",
  "background": {
    "description": "第二次世界大战期间伦敦拥挤的火车站疏散场景。蒸汽和烟雾弥漫在空气中，孩子们被送往乡下躲避空袭。",
    "era": "1940 年代战时英国",
    "location": "伦敦火车站站台"
  },
  "characters": ["佩文西夫人", "露西·佩文西"],
  "camera": {
    "type": "特写双人镜头",
    "movement": "静态带轻微手持运动",
    "angle": "侧面视角，亲密构图",
    "focus": "两张脸都清晰对焦，背景虚化"
  },
  "dialogue": [
    {
      "character": "佩文西夫人",
      "text": "你必须为我勇敢，亲爱的。我会来找你... 我保证。"
    },
    {
      "character": "露西·佩文西",
      "text": "我会的，母亲。我保证。"
    }
  ],
  "audio": [
    {
      "type": "火车汽笛声（表示出发）",
      "volume": 1
    },
    {
      "type": "弦乐逐渐增强情绪，然后渐弱",
      "volume": 0.5
    },
    {
      "type": "火车站环境音",
      "volume": 0.5
    }
  ]
}
```

第 3 步：使用图像生成技能生成参考图像

加载图像生成技能，根据技能生成单个参考图像 `narnia-farewell-scene-01.jpg`。

第 4 步：使用 generate.py 脚本生成视频
```bash
python /mnt/skills/public/video-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/narnia-farewell-scene.json \
  --reference-images /mnt/user-data/outputs/narnia-farewell-scene-01.jpg \
  --output-file /mnt/user-data/outputs/narnia-farewell-scene-01.mp4 \
  --aspect-ratio 16:9
```
> 不要读取 python 文件，只需用参数调用它。

## 输出处理

生成后：

- 视频通常保存在 `/mnt/user-data/outputs/`
- 使用 `present_files` 工具将生成的视频（优先）以及生成的图像（如果适用）分享给用户
- 提供生成结果的简要描述
- 如需调整，提供迭代机会

## 注意事项

- 无论用户语言如何，始终使用英语编写提示
- JSON 格式确保结构化、可解析的提示
- 参考图像显著提升生成质量
- 迭代优化是获得最佳结果的正常过程

## 提供者（Gemini / MiniMax）

提供者凭证从运行时环境读取，而不是嵌入在脚本中。不要将它们的值放在提示文件或命令行参数中。

由环境变量自动选择（CLI 不变）：

- `GEMINI_API_KEY` 设置 → Gemini Veo（默认，不变）。
- 仅设置 `MINIMAX_API_KEY` → MiniMax 视频（`/v1/video_generation`，异步 3 步轮询/下载）。
- 强制使用 `VIDEO_GENERATION_PROVIDER=gemini|minimax`。

MiniMax 覆盖：`MINIMAX_API_HOST`（默认 `https://api.minimaxi.com`），`MINIMAX_VIDEO_MODEL`（默认 `MiniMax-Hailuo-2.3`）。第一个参考图像用作 MiniMax `first_frame_image`。MiniMax 忽略 `--aspect-ratio`（它使用分辨率/时长）。
