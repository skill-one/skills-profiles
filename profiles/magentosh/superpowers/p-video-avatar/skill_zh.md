> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# Pruna P-Video-Avatar

通过 [inference.sh](https://inference.sh) CLI 从单张肖像图像生成口播头像视频。

P-Video-Avatar 是最快且最具成本效益的头像视频模型。质量与 Veo 3.0 相当，比 Fabric、OmniHuman 和 HeyGen 等替代方案快 18 倍且便宜 6 倍。

## 快速入门

> 需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 从肖像 + 文本脚本生成头像
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "你好，欢迎参加我们的产品演示！",
  "voice": "Zephyr (女声)"
}'
```

## 完整工作流程：生成肖像 + 头像视频

使用 Pruna P-Image 生成肖像，然后使用 P-Video-Avatar 动画化它：

```bash
# 1. 使用 P-Image 生成肖像图像
belt app run pruna/p-image --input '{
  "prompt": "专业正面肖像照，年轻女性，中性背景，看向镜头，工作室灯光，照片级真实感",
  "aspect_ratio": "9:16"
}'

# 2. 使用生成的图像 URL 创建头像视频
belt app run pruna/p-video-avatar --input '{
  "image": "<步骤1中的图像URL>",
  "voice_script": "大家好！让我带你们了解我们最新的功能。",
  "voice": "Zephyr (女声)",
  "resolution": "720p"
}'
```

## 示例

### 带语音选择的文本脚本

```bash
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "欢迎参加我们的产品演示。今天我将向您展示三个关键功能。",
  "voice": "Puck (男声)",
  "voice_language": "英语 (美国)",
  "resolution": "720p"
}'
```

### 音频驱动头像

提供您自己的音频文件而不是使用内置的 TTS：

```bash
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "audio": "https://speech.mp3"
}'
```

当同时提供 `audio` 和 `voice_script` 时，音频优先。

### 1080p 带自定义风格

```bash
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "这对我们的社区来说是个激动人心的消息！",
  "voice": "Aoede (女声)",
  "voice_prompt": "热情且充满活力的语调，节奏稍快",
  "video_prompt": "该人物正在舞台上演讲，灯光戏剧化",
  "resolution": "1080p"
}'
```

### 多语言内容

```bash
# 西班牙语
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "Bienvenidos a nuestra demostración de producto.",
  "voice": "Kore (女声)",
  "voice_language": "西班牙语"
}'

# 日语
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "こんにちは、製品デモへようこそ。",
  "voice": "Leda (女声)",
  "voice_language": "日语"
}'
```

### 可重复生成

```bash
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "每次结果都一致。",
  "seed": 42
}'
```

## 可用语音

**女性：** Zephyr、Kore、Leda、Aoede、Callirrhoe、Autonoe、Despina、Erinome、Laomedeia、Achernar、Gacrux、Pulcherrima、Vindemiatrix、Sulafat

**男性：** Puck、Charon、Fenrir、Orus、Enceladus、Iapetus、Umbriel、Algenib、Algieba、Schedar、Achird、Zubenelgenubi、Sadachbia、Sadaltager、Alnilam、Rasalgethi

## 支持的语言

英语 (美国)、英语 (英国)、西班牙语、法语、德语、意大利语、葡萄牙语 (巴西)、日语、韩语、印地语

## 参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `image` | 文件 | 必填 | 肖像图像 (jpg, jpeg, png, webp) |
| `voice_script` | 字符串 | - | 人物要说的话 |
| `audio` | 文件 | - | 音频文件 (覆盖 voice_script) |
| `voice` | 字符串 | "Zephyr (女声)" | 语音选择 |
| `voice_language` | 字符串 | "英语 (美国)" | 输出语言 |
| `resolution` | 字符串 | "720p" | 720p 或 1080p |
| `video_prompt` | 字符串 | "该人物正在说话。" | 控制头像行为和背景 |
| `voice_prompt` | 字符串 | "说以下内容。" | 控制语调、节奏、情感 |
| `seed` | 整数 | 随机 | 可重复生成 |
| `disable_safety_filter` | 布尔值 | true | 禁用内容过滤器 |
| `disable_prompt_upsampling` | 布尔值 | false | 跳过提示增强 |

## 定价

| 分辨率 | 价格 |
|--------|------|
| 720p | 每秒输出视频 0.025 美元 |
| 1080p | 每秒输出视频 0.045 美元 |

示例：30 秒 720p 视频 = 0.75 美元

### 免费启动周末

**P-Video-Avatar 从 2026 年 5 月 1 日下午 4:00 CET 至 2026 年 5 月 4 日晚上 11:59 CET 完全免费。** 在此窗口期内所有费用均由我们承担——无账单，无分辨率限制。

## 竞争优势

| 功能 | P-Video-Avatar | Fabric 1.0 | OmniHuman 1.5 | HeyGen Avatar 4 |
|------|---------------|------------|---------------|-----------------|
| 速度 (每秒视频) | ~1.83s/s | ~34s/s (慢 18 倍) | ~28s/s (慢 15 倍) | ~26s/s (慢 14 倍) |
| 每秒成本 | 0.025 美元 | 0.14 美元 (贵 5.6 倍) | 0.16 美元 (贵 6.4 倍) | 0.075 美元 (贵 3 倍) |
| 内置 TTS | 是 | 是 | 否 | 是 |
| 动态背景 | 是 | 是 | 否 | 是 |
| 1080p 支持 | 是 | 否 | 否 | 是 |

## 应用场景

- **营销**：产品演示、UGC 风格广告，AI 呈现者
- **教育**：课程视频、解释视频、辅导内容
- **本地化**：从一张图像中为 10 种语言配音
- **社交媒体**：一致的虚拟影响者内容
- **企业**：培训、入职、公告
- **游戏**：角色头像、NPC 对话视频
- **客户支持**：个性化视频回复

## 小贴士

- 使用高质量的肖像照片（正面、良好光线）
- 输出视频的宽高比与输入图像匹配
- 使用 `video_prompt` 控制动态背景和肢体语言
- 使用 `voice_prompt` 控制说话风格、情感和节奏
- 保持视频在 3 分钟以内以获得最佳视觉一致性
- 使用 `pruna/p-image` 生成肖像，使用宽高比 `9:16` 以生成垂直头像视频

## 相关 Pruna 模型

```bash
# 生成肖像图像
belt app run pruna/p-image --input '{"prompt": "专业正面肖像照"}'

# 一般视频生成
belt app run pruna/p-video --input '{"prompt": "电影场景"}'

# 图像编辑
belt app run pruna/p-image-edit --input '{"prompt": "更换背景", "image": "https://photo.jpg"}'
```

## 相关技能

```bash
# 完整平台技能 (所有应用)
npx skills add inference-sh/skills@infsh-cli

# Pruna 视频生成
npx skills add inference-sh/skills@p-video

# Pruna 图像生成
npx skills add inference-sh/skills@p-image

# 所有视频生成模型
npx skills add inference-sh/skills@ai-video-generation

# 图像生成 (用于创建肖像)
npx skills add inference-sh/skills@ai-image-generation
```

浏览所有 Pruna 应用：`belt app list --search "pruna"`

## 文档

- [运行应用](https://inference.sh/docs/apps/running) - 通过 CLI 运行应用
- [流式传输结果](https://inference.sh/docs/api/sdk/streaming) - 实时进度更新
- [内容管道示例](https://inference.sh/docs/examples/content-pipeline) - 构建媒体工作流
